import requests
import json
from config import Config
import streamlit as st

class WatsonxLLMService:
    """IBM Watsonx Granite LLM service integration"""
    
    def __init__(self):
        self.api_key = Config.WATSONX_API_KEY
        self.project_id = Config.WATSONX_PROJECT_ID
        self.base_url = Config.WATSONX_URL
        self.access_token = None
        self._get_access_token()
    
    def _get_access_token(self):
        """Get access token for Watsonx API"""
        try:
            if not self.api_key:
                raise ValueError("Watsonx API key not found in configuration")

            token_url = "https://iam.cloud.ibm.com/identity/token"
            headers = {
                "Content-Type": "application/x-www-form-urlencoded"
            }
            data = {
                "grant_type": "urn:ibm:params:oauth:grant-type:apikey",
                "apikey": self.api_key
            }

            response = requests.post(token_url, headers=headers, data=data, timeout=15)
            # If unauthorized or other error, try to surface the reason
            try:
                response.raise_for_status()
            except Exception:
                details = None
                try:
                    details = response.json()
                except Exception:
                    details = response.text
                st.error(f"Failed to get Watsonx access token: HTTP {response.status_code} - {details}")
                self.access_token = None
                return

            token_data = response.json()
            self.access_token = token_data.get("access_token")

        except Exception as e:
            st.error(f"Failed to get Watsonx access token: {str(e)}")
            self.access_token = None
    
    def _get_tone_prompt(self, tone: str, text: str) -> str:
        """Generate appropriate prompt based on selected tone"""
        
        tone_prompts = {
            'Neutral': f"""Rewrite the following text in a clear, neutral, and professional tone. 
            Maintain the original meaning and key information while making it suitable for audio narration.
            Keep the same length and structure.
            
            Original text: {text}
            
            Rewritten text:""",
            
            'Suspenseful': f"""Rewrite the following text in a suspenseful and engaging tone. 
            Add dramatic tension and intrigue while maintaining the original meaning and information.
            Use compelling language that builds anticipation and keeps listeners engaged.
            
            Original text: {text}
            
            Rewritten text:""",
            
            'Inspiring': f"""Rewrite the following text in an inspiring and motivational tone.
            Transform the content to be uplifting, encouraging, and empowering while preserving the original meaning.
            Use positive language that motivates and energizes the listener.
            
            Original text: {text}
            
            Rewritten text:"""
        }
        
        return tone_prompts.get(tone, tone_prompts['Neutral'])
    
    def rewrite_text(self, text: str, tone: str = 'Neutral') -> str:
        """
        Rewrite text using Watsonx Granite LLM with specified tone
        
        Args:
            text (str): Original text to rewrite
            tone (str): Tone to apply ('Neutral', 'Suspenseful', 'Inspiring')
            
        Returns:
            str: Rewritten text in specified tone
        """
        if not self.access_token:
            raise Exception("Watsonx service not properly initialized")
        
        try:
            # Prepare the prompt
            prompt = self._get_tone_prompt(tone, text)
            
            # API endpoint for text generation (current path format)
            url = f"{self.base_url}/ml/v1/text/generation?version=2023-05-29"
            
            headers = {
                "Accept": "application/json",
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.access_token}"
            }
            
            # Request payload
            payload = {
                "input": prompt,
                "parameters": {
                    "decoding_method": "greedy",
                    "max_new_tokens": 500,
                    "min_new_tokens": 50,
                    "stop_sequences": [],
                    "repetition_penalty": 1.1
                },
                "model_id": "ibm/granite-13b-chat-v2",
                "project_id": self.project_id
            }
            
            # Make the request
            response = requests.post(url, headers=headers, json=payload)
            response.raise_for_status()
            
            # Parse response
            result = response.json()
            
            if 'results' in result and len(result['results']) > 0:
                generated_text = result['results'][0]['generated_text'].strip()
                return generated_text
            else:
                raise Exception("No text generated from Watsonx API")
                
        except Exception as e:
            st.error(f"Error rewriting text with Watsonx: {str(e)}")
            # Return original text as fallback
            return text
    
    def is_service_available(self) -> bool:
        """Check if the service is properly initialized"""
        return bool(self.api_key and self.project_id and self.base_url and self.access_token)
