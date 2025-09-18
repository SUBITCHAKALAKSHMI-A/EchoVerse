from config import Config
import streamlit as st
from typing import Optional

try:
    # Optional: used when calling a Space endpoint
    from gradio_client import Client
except Exception:  # pragma: no cover
    Client = None


class HuggingFaceLLMService:
    """Hugging Face integration for tone-based text rewriting.

    Uses a Hugging Face Space endpoint via gradio_client (no direct HTTP model calls).
    """

    def __init__(self, model_id: Optional[str] = None, space_id: Optional[str] = None, space_api_name: Optional[str] = None):
        # Space config (from user's message)
        # Example Space: "sabarnakb/GraniteEchoverse" with api_name "/process_text"
        self.space_id = space_id or Config.HF_SPACE_ID
        self.space_api_name = space_api_name or Config.HF_SPACE_API_NAME

        self.token = Config.HUGGINGFACE_TOKEN

    def is_service_available(self) -> bool:
        return bool(self.token and self.space_id and Client is not None)

    def _get_tone_prompt(self, tone: str, text: str) -> str:
        tone_prompts = {
            'Neutral': (
                "You are a professional editor for audiobooks. Rewrite the text in a clear, neutral, and professional tone. "
                "Maintain original meaning and key information. Keep a similar length and structure.\n\n"
                f"Original text:\n{text}\n\nRewritten text:"
            ),
            'Suspenseful': (
                "You are a creative writer. Rewrite the text in a suspenseful and engaging tone. Add dramatic tension and intrigue "
                "without changing the meaning. Use compelling language that builds anticipation. Keep a similar length.\n\n"
                f"Original text:\n{text}\n\nRewritten text:"
            ),
            'Inspiring': (
                "You are an inspirational speaker. Rewrite the text in an inspiring and motivational tone. Keep the original meaning, "
                "use uplifting language that energizes the listener. Keep a similar length.\n\n"
                f"Original text:\n{text}\n\nRewritten text:"
            ),
        }
        return tone_prompts.get(tone, tone_prompts['Neutral'])

    def rewrite_text(self, text: str, tone: str = 'Neutral') -> str:
        if not self.is_service_available():
            raise Exception("Hugging Face token not configured")

        try:
            if Client is not None and self.space_id:
                tone_map = {
                    'Neutral': 'neutral',
                    'Suspenseful': 'suspenseful',
                    'Inspiring': 'inspiring',
                }
                mapped_tone = tone_map.get(tone, 'neutral')
                client = Client(self.space_id, hf_token=self.token)
                # Simple cold-start retry
                for attempt in range(2):
                    try:
                        result = client.predict(
                            input_text=text,
                            selected_tone=mapped_tone,
                            api_name=self.space_api_name,
                        )
                        # Normalize result to string
                        if isinstance(result, str):
                            if result.strip():
                                return result.strip()
                        elif isinstance(result, (list, tuple)) and result:
                            # Some Spaces return a list of outputs; find first string-like
                            for item in result:
                                if isinstance(item, str) and item.strip():
                                    return item.strip()
                        elif isinstance(result, dict):
                            # Try common keys
                            for key in ("text", "generated_text", "data", "output"):
                                val = result.get(key)
                                if isinstance(val, str) and val.strip():
                                    return val.strip()
                        # If format not recognized, break to fallback
                        break
                    except Exception:
                        if attempt == 0:
                            # retry once (Space may be waking up)
                            continue
                        # Attempt to dynamically resolve endpoint and call again
                        try:
                            info = client.view_api()
                            # Try named endpoint mapping first
                            api_name = None
                            fn_index = None
                            if isinstance(info, dict):
                                # gradio_client >=0.10 style
                                named = (info.get('named_endpoints') or {})
                                if named:
                                    # pick any with two params matching names
                                    for name, meta in named.items():
                                        params = [p.get('name','').lower() for p in (meta.get('parameters') or [])]
                                        if 'input_text' in params and 'selected_tone' in params:
                                            api_name = name
                                            break
                                    if not api_name:
                                        # fallback to provided api_name if exists in named
                                        if self.space_api_name in named:
                                            api_name = self.space_api_name
                                # If no named endpoints, try function indices
                                if not api_name:
                                    apis = info.get('endpoints') or []
                                    for ep in apis:
                                        params = [p.get('name','').lower() for p in (ep.get('parameters') or [])]
                                        if 'input_text' in params and 'selected_tone' in params:
                                            fn_index = ep.get('fn_index')
                                            break
                            # Try calling with resolved api
                            if api_name:
                                result = client.predict(
                                    input_text=text,
                                    selected_tone=mapped_tone,
                                    api_name=api_name,
                                )
                            elif fn_index is not None:
                                result = client.predict(
                                    input_text=text,
                                    selected_tone=mapped_tone,
                                    fn_index=fn_index,
                                )
                            else:
                                raise RuntimeError("Could not resolve Space endpoint parameters")
                            # Normalize as before
                            if isinstance(result, str) and result.strip():
                                return result.strip()
                            if isinstance(result, (list, tuple)):
                                for item in result:
                                    if isinstance(item, str) and item.strip():
                                        return item.strip()
                            if isinstance(result, dict):
                                for key in ("text", "generated_text", "data", "output"):
                                    val = result.get(key)
                                    if isinstance(val, str) and val.strip():
                                        return val.strip()
                        except Exception:
                            # give up, report error below
                            pass
        except Exception as e:
            st.error(f"Hugging Face Space call failed: {e}")
            return text
