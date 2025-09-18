import streamlit as st
import os
from datetime import datetime
from config import Config
from services.watson_tts import WatsonTTSService
from services.hf_llm import HuggingFaceLLMService
from app_restored import (
    save_to_library,
    save_bookmark,
    save_bookmark_from_bytes,
    create_empty_bookmark,
    attach_audio_to_bookmark,
    load_bookmarks_from_disk,
    load_library_from_disk,
)

# -------- Modern UI from new.py (trimmed and adapted) --------

def inject_modern_css():
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
        :root { --primary-color:#6366f1; --primary-hover:#4f46e5; --surface-primary:#ffffff; --surface-secondary:#f8fafc; --surface-tertiary:#f1f5f9; --text-primary:#0f172a; --text-secondary:#64748b; --border-color:#e2e8f0; --border-hover:#cbd5e1; --radius-md:8px; --shadow-sm:0 1px 2px 0 rgb(0 0 0 / 0.05); --shadow-md:0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1);} 
        *{ font-family:'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; }
        html, body, [data-testid="stAppViewContainer"]{ background:var(--surface-secondary)!important; color:var(--text-primary)!important; }
        [data-testid="stSidebar"]{ background:var(--surface-primary)!important; border-right:1px solid var(--border-color)!important; box-shadow:0 10px 15px -3px rgb(0 0 0 / 0.1); }
        .main .block-container{ max-width:1200px!important; padding:2rem 1rem!important; }
        .modern-card{ background:var(--surface-primary); border:1px solid var(--border-color); border-radius:12px; box-shadow:var(--shadow-md); padding:1.25rem; margin-bottom:1rem; }
        .app-title{ font-size:2rem; font-weight:700; background:linear-gradient(135deg, var(--primary-color), #10b981); -webkit-background-clip:text; -webkit-text-fill-color:transparent; }
        .section-title{ font-size:1.1rem; font-weight:600; margin: 1rem 0 0.5rem; }
        .stButton > button{ background:var(--surface-primary)!important; color:var(--text-primary)!important; border:1px solid var(--border-color)!important; border-radius:var(--radius-md)!important; box-shadow:var(--shadow-sm)!important; }
        .stButton > button[kind="primary"]{ background:var(--primary-color)!important; color:#fff!important; border-color:var(--primary-color)!important; }
        </style>
        """,
        unsafe_allow_html=True,
    )


def header():
    st.markdown("<div class='app-title'>🎧 EchoVerse</div>", unsafe_allow_html=True)
    st.caption("AI-Powered Audiobook Creator")


# -------- Services --------
@st.cache_resource
def initialize_services():
    tts_service = WatsonTTSService()
    llm_service = HuggingFaceLLMService()
    return tts_service, llm_service


# -------- Pages --------

def page_create(tts_service, llm_service):
    header()

    # Project meta
    with st.container():
        st.markdown("<div class='section-title'>📝 Project Setup</div>", unsafe_allow_html=True)
        col1, col2 = st.columns([2,1])
        with col1:
            project_name = st.text_input("Project Name", placeholder="Enter your audiobook title…")
        with col2:
            project_description = st.text_input("Description", placeholder="Short description…")

    # Text input
    st.markdown("<div class='section-title'>📖 Text Input</div>", unsafe_allow_html=True)
    method = st.radio("Input method", ["Type/Paste", "Upload .txt"], horizontal=True)
    user_text = ""
    if method == "Type/Paste":
        user_text = st.text_area("Enter your text", height=220, placeholder="Paste your text here…")
    else:
        up = st.file_uploader("Upload .txt", type=["txt"])
        if up is not None:
            user_text = up.read().decode("utf-8", errors="ignore")
            st.text_area("Preview", user_text, height=160, disabled=True)

    if not user_text.strip():
        st.info("Enter some text to proceed.")
        return

    # Tone + rewrite
    st.markdown("<div class='section-title'>🎭 Tone & Rewrite</div>", unsafe_allow_html=True)
    c1, c2 = st.columns([2,1])
    with c1:
        selected_tone = st.selectbox("Narration Tone", Config.TONE_OPTIONS)
    with c2:
        if st.button("🔄 Suggest Rewrite", type="primary"):
            if llm_service.is_service_available():
                with st.spinner("Rewriting text with AI…"):
                    rewritten_text = llm_service.rewrite_text(user_text, selected_tone)
                    st.session_state.rewritten_text = rewritten_text
                    st.success("Text rewritten successfully!")
            else:
                st.error("LLM service not available. Check your Hugging Face settings.")

    if 'rewritten_text' in st.session_state:
        st.markdown("### 📋 Before & After")
        colL, colR = st.columns(2)
        with colL:
            st.text_area("Original", user_text, height=260, disabled=True)
        with colR:
            updated = st.text_area("Rewritten", st.session_state.rewritten_text, height=260)
            st.session_state.rewritten_text = updated

    # Voice & TTS
    st.markdown("<div class='section-title'>🎤 Voice & Audio</div>", unsafe_allow_html=True)
    v1, v2, v3 = st.columns([2,1,1])
    with v1:
        voices = tts_service.get_available_voices()
        selected_voice = st.selectbox("Voice", voices)
    with v2:
        gen_audio = st.button("🎵 Generate Audio", type="primary")
    with v3:
        if project_name:
            if st.button("💾 Save to Library"):
                save_to_library(
                    project_name,
                    project_description,
                    user_text,
                    st.session_state.get('rewritten_text', user_text),
                    selected_tone,
                    selected_voice,
                )

    effective_text = st.session_state.get('rewritten_text', user_text)
    if gen_audio:
        if tts_service.is_service_available():
            with st.spinner("Generating audio…"):
                try:
                    audio_bytes = tts_service.synthesize_speech(effective_text, selected_voice)
                    st.session_state.audio_data = audio_bytes
                    st.success("Audio generated!")
                except Exception as e:
                    st.error(f"TTS error: {e}")
        else:
            st.error("TTS service not available. Check IBM Watson TTS config.")

    # Playback / download / bookmark
    if 'audio_data' in st.session_state:
        st.audio(st.session_state.audio_data, format='audio/mp3')
        st.download_button(
            label="⬇️ Download MP3",
            data=st.session_state.audio_data,
            file_name=f"{project_name or 'audiobook'}.mp3",
            mime="audio/mp3",
        )
        st.markdown("### 🔖 Add Bookmark")
        bc1, bc2 = st.columns([2,1])
        with bc1:
            bm_name = st.text_input("Bookmark Name", value=project_name or 'Untitled')
        with bc2:
            if st.button("➕ Save as Bookmark"):
                save_bookmark(
                    name=bm_name,
                    source_project=project_name or 'Untitled',
                    text_snippet=(st.session_state.get('rewritten_text') or user_text)[:280],
                    tone=selected_tone,
                    voice=selected_voice,
                )
    else:
        st.markdown("### 🔖 Create Bookmark (no audio yet)")
        bc1, bc2 = st.columns([2,1])
        with bc1:
            bm_name2 = st.text_input("Bookmark Name", value=project_name or 'Untitled')
        with bc2:
            if st.button("➕ Create Empty Bookmark"):
                create_empty_bookmark(
                    name=bm_name2,
                    source_project=project_name or 'Untitled',
                    text_snippet=(st.session_state.get('rewritten_text') or user_text)[:280],
                    tone=selected_tone,
                    voice=selected_voice,
                )


def page_library():
    header()
    st.markdown("<div class='section-title'>📚 Your Library</div>", unsafe_allow_html=True)
    if 'library_loaded' not in st.session_state:
        load_library_from_disk()
    items = st.session_state.get('library') or []
    if not items:
        st.info("No projects saved yet.")
        return
    for i, p in enumerate(items):
        with st.expander(f"📖 {p.get('name','Project')} "):
            st.write(f"Description: {p.get('description','')}")
            st.write(f"Tone: {p.get('tone','')} | Voice: {p.get('voice','')}")
            st.write(f"Created: {p.get('created_at','')}")
            # texts
            col1, col2 = st.columns(2)
            with col1:
                st.text_area("Original", p.get('original_text',''), height=120, key=f"orig_{i}")
            with col2:
                st.text_area("Rewritten", p.get('rewritten_text',''), height=120, key=f"rew_{i}")
            # audio
            ap = (p.get('paths') or {}).get('audio')
            if ap and os.path.exists(ap):
                with open(ap, 'rb') as f:
                    ab = f.read()
                st.audio(ab, format='audio/mp3')
                st.download_button("⬇️ Download MP3", ab, os.path.basename(ap), mime="audio/mp3", key=f"dl_{i}")
                # Add to bookmarks from project audio
                st.markdown("#### Add to Bookmarks")
                c1, c2 = st.columns([2,1])
                with c1:
                    bm_name = st.text_input("Bookmark Name", value=p.get('name') or 'Project', key=f"bm_from_proj_{i}")
                with c2:
                    if st.button("➕ Add to Bookmarks", key=f"add_bm_{i}"):
                        try:
                            with open(ap, 'rb') as f:
                                audio_bytes = f.read()
                            snippet = (p.get('rewritten_text') or p.get('original_text') or '')[:280]
                            save_bookmark_from_bytes(
                                name=bm_name,
                                source_project=p.get('name') or 'Project',
                                text_snippet=snippet,
                                tone=p.get('tone',''),
                                voice=p.get('voice',''),
                                audio_bytes=audio_bytes,
                            )
                            st.success("Bookmark saved from project audio.")
                        except Exception as e:
                            st.error(f"Failed to add bookmark: {e}")


def page_bookmarks():
    header()
    st.markdown("<div class='section-title'>🔖 Your Bookmarks</div>", unsafe_allow_html=True)
    if 'bookmarks_loaded' not in st.session_state:
        load_bookmarks_from_disk()
    bms = st.session_state.get('bookmarks') or []
    if not bms:
        st.info("No bookmarks yet.")
        return
    for i, bm in enumerate(bms):
        with st.expander(f"🔖 {bm.get('name','Bookmark')} - {bm.get('source_project','')}"):
            st.write(f"Tone: {bm.get('tone','')} | Voice: {bm.get('voice','')}")
            st.write(f"Created: {bm.get('created_at','')}")
            st.text_area("Snippet", bm.get('text_snippet') or '', height=100, key=f"bm_snip_{i}")
            ap = (bm.get('paths') or {}).get('audio')
            if ap and os.path.exists(ap):
                with open(ap, 'rb') as f:
                    ab = f.read()
                st.audio(ab, format='audio/mp3')
                st.download_button("⬇️ Download Bookmark MP3", ab, os.path.basename(ap), mime="audio/mp3", key=f"bm_dl_{i}")
            else:
                st.caption("No audio attached yet.")
                if 'audio_data' in st.session_state:
                    if st.button("📎 Attach Current Audio", key=f"bm_attach_{i}"):
                        attach_audio_to_bookmark(bm)


def page_settings(tts_service, llm_service):
    header()
    st.markdown("<div class='section-title'>⚙️ Settings</div>", unsafe_allow_html=True)
    st.write("TTS Connected:" , tts_service.is_service_available())
    st.write("Rewriter Connected:", llm_service.is_service_available())
    st.write("Library Dir:", Config.LIBRARY_DIR)
    st.write("Bookmarks Dir:", Config.BOOKMARKS_DIR)


# -------- App --------
st.set_page_config(page_title="EchoVerse - Modern", page_icon="🎧", layout="wide")
inject_modern_css()

def main():
    tts_service, llm_service = initialize_services()
    if 'bookmarks_loaded' not in st.session_state:
        load_bookmarks_from_disk()
    if 'library_loaded' not in st.session_state:
        load_library_from_disk()

    with st.sidebar:
        st.markdown("### 🎧 EchoVerse")
        st.markdown("---")
        if 'current_page' not in st.session_state:
            st.session_state.current_page = "Create"
        if st.button("✨ Create Audio", use_container_width=True):
            st.session_state.current_page = "Create"
        if st.button("📚 Library", use_container_width=True):
            st.session_state.current_page = "Library"
        if st.button("🔖 Bookmarks", use_container_width=True):
            st.session_state.current_page = "Bookmarks"
        if st.button("⚙️ Settings", use_container_width=True):
            st.session_state.current_page = "Settings"
        st.markdown("---")
        st.caption("Services")
        st.write("TTS:", "✅" if tts_service.is_service_available() else "❌")
        st.write("Rewriter:", "✅" if llm_service.is_service_available() else "❌")

    page = st.session_state.current_page
    if page == "Create":
        page_create(tts_service, llm_service)
    elif page == "Library":
        page_library()
    elif page == "Bookmarks":
        page_bookmarks()
    else:
        page_settings(tts_service, llm_service)


if __name__ == "__main__":
    main()
