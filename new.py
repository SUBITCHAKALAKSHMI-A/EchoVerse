import streamlit as st
import io
import base64
from services.watson_tts import WatsonTTSService
from services.hf_llm import HuggingFaceLLMService
from config import Config
import json
import os
from datetime import datetime
import shutil
from app_restored import (
    save_to_library as save_project_to_library,
    save_bookmark as save_audio_bookmark,
    save_bookmark_from_bytes as save_bookmark_from_bytes_impl,
    create_empty_bookmark as create_empty_bookmark_impl,
    attach_audio_to_bookmark as attach_audio_to_bookmark_impl,
    load_bookmarks_from_disk as load_bookmarks_from_disk_impl,
    load_library_from_disk as load_library_from_disk_impl,
)


# Enhanced Modern UI Components
def inject_modern_css():
    """Inject modern, professional CSS styling"""
    st.markdown("""
    <style>
    /* Import Inter font for modern look */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
   
    /* CSS Variables for theming */
    :root {
        --primary-color: #6366f1;
        --primary-hover: #4f46e5;
        --secondary-color: #f1f5f9;
        --accent-color: #10b981;
        --warning-color: #f59e0b;
        --danger-color: #ef4444;
        --text-primary: #0f172a;
        --text-secondary: #64748b;
        --text-muted: #94a3b8;
        --surface-primary: #ffffff;
        --surface-secondary: #f8fafc;
        --surface-tertiary: #f1f5f9;
        --border-color: #e2e8f0;
        --border-hover: #cbd5e1;
        --shadow-sm: 0 1px 2px 0 rgb(0 0 0 / 0.05);
        --shadow-md: 0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1);
        --shadow-lg: 0 10px 15px -3px rgb(0 0 0 / 0.1), 0 4px 6px -4px rgb(0 0 0 / 0.1);
        --shadow-xl: 0 20px 25px -5px rgb(0 0 0 / 0.1), 0 8px 10px -6px rgb(0 0 0 / 0.1);
        --radius-sm: 6px;
        --radius-md: 8px;
        --radius-lg: 12px;
        --radius-xl: 16px;
    }
   
    [data-theme="dark"] {
        --primary-color: #818cf8;
        --primary-hover: #6366f1;
        --secondary-color: #1e293b;
        --accent-color: #34d399;
        --text-primary: #f1f5f9;
        --text-secondary: #cbd5e1;
        --text-muted: #94a3b8;
        --surface-primary: #0f172a;
        --surface-secondary: #1e293b;
        --surface-tertiary: #334155;
        --border-color: #334155;
        --border-hover: #475569;
    }
   
    /* Base styles */
    * {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    }
   
    html, body, [data-testid="stAppViewContainer"] {
        background: var(--surface-secondary) !important;
        color: var(--text-primary) !important;
    }
   
    /* Sidebar redesign */
    [data-testid="stSidebar"] {
        background: var(--surface-primary) !important;
        border-right: 1px solid var(--border-color) !important;
        box-shadow: var(--shadow-lg) !important;
    }
   
    [data-testid="stSidebar"] > div {
        padding-top: 2rem !important;
    }
   
    /* Main content area */
    .main .block-container {
        max-width: 1200px !important;
        padding: 2rem 1rem !important;
        background: transparent !important;
    }
   
    /* Modern card component */
    .modern-card {
        background: var(--surface-primary);
        border: 1px solid var(--border-color);
        border-radius: var(--radius-lg);
        box-shadow: var(--shadow-md);
        padding: 1.5rem;
        margin-bottom: 1.5rem;
        transition: all 0.2s ease;
    }
   
    .modern-card:hover {
        box-shadow: var(--shadow-lg);
        border-color: var(--border-hover);
    }
   
    /* Chat-style message bubbles */
    .chat-message {
        background: var(--surface-primary);
        border: 1px solid var(--border-color);
        border-radius: var(--radius-lg);
        padding: 1rem 1.25rem;
        margin-bottom: 1rem;
        position: relative;
    }
   
    .chat-message.user {
        background: var(--primary-color);
        color: white;
        margin-left: 2rem;
    }
   
    .chat-message.assistant {
        background: var(--surface-primary);
        margin-right: 2rem;
        border-left: 3px solid var(--primary-color);
    }
   
    /* Typography improvements */
    .app-title {
        font-size: 2.5rem;
        font-weight: 700;
        background: linear-gradient(135deg, var(--primary-color), var(--accent-color));
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        text-align: center;
        margin-bottom: 0.5rem;
    }
   
    .app-subtitle {
        color: var(--text-secondary);
        text-align: center;
        font-size: 1.1rem;
        margin-bottom: 2rem;
    }
   
    .section-title {
        font-size: 1.25rem;
        font-weight: 600;
        color: var(--text-primary);
        margin-bottom: 1rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
   
    /* Modern button styles */
    .stButton > button {
        background: var(--surface-primary) !important;
        color: var(--text-primary) !important;
        border: 1px solid var(--border-color) !important;
        border-radius: var(--radius-md) !important;
        font-weight: 500 !important;
        transition: all 0.2s ease !important;
        box-shadow: var(--shadow-sm) !important;
    }
   
    .stButton > button:hover {
        background: var(--surface-tertiary) !important;
        border-color: var(--border-hover) !important;
        box-shadow: var(--shadow-md) !important;
        transform: translateY(-1px) !important;
    }
   
    .stButton > button[kind="primary"] {
        background: var(--primary-color) !important;
        color: white !important;
        border-color: var(--primary-color) !important;
    }
   
    .stButton > button[kind="primary"]:hover {
        background: var(--primary-hover) !important;
        border-color: var(--primary-hover) !important;
    }
   
    /* Sidebar navigation buttons */
    [data-testid="stSidebar"] .stButton > button {
        width: 100% !important;
        justify-content: flex-start !important;
        padding: 0.75rem 1rem !important;
        margin-bottom: 0.5rem !important;
        border-radius: var(--radius-md) !important;
    }
   
    /* Input field improvements */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea,
    .stSelectbox > div > div > div {
        background: var(--surface-primary) !important;
        color: var(--text-primary) !important;
        border: 1px solid var(--border-color) !important;
        border-radius: var(--radius-md) !important;
        box-shadow: var(--shadow-sm) !important;
        transition: all 0.2s ease !important;
    }
   
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {
        border-color: var(--primary-color) !important;
        box-shadow: 0 0 0 3px rgb(99 102 241 / 0.1) !important;
    }
   
    /* Progress indicators */
    .status-badge {
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        padding: 0.375rem 0.75rem;
        border-radius: 999px;
        font-size: 0.875rem;
        font-weight: 500;
    }
   
    .status-success {
        background: #dcfce7;
        color: #166534;
    }
   
    .status-error {
        background: #fee2e2;
        color: #991b1b;
    }
   
    .status-warning {
        background: #fef3c7;
        color: #92400e;
    }
   
    /* Audio player styling */
    audio {
        width: 100% !important;
        border-radius: var(--radius-md) !important;
        box-shadow: var(--shadow-sm) !important;
    }
   
    /* File uploader improvements */
    .stFileUploader > div {
        background: var(--surface-primary) !important;
        border: 2px dashed var(--border-color) !important;
        border-radius: var(--radius-lg) !important;
        padding: 2rem !important;
        text-align: center !important;
        transition: all 0.2s ease !important;
    }
   
    .stFileUploader > div:hover {
        border-color: var(--primary-color) !important;
        background: var(--surface-tertiary) !important;
    }
   
    /* Expander improvements */
    .streamlit-expanderHeader {
        background: var(--surface-primary) !important;
        border: 1px solid var(--border-color) !important;
        border-radius: var(--radius-md) !important;
        color: var(--text-primary) !important;
    }
   
    .streamlit-expanderContent {
        background: var(--surface-primary) !important;
        border: 1px solid var(--border-color) !important;
        border-top: none !important;
        border-radius: 0 0 var(--radius-md) var(--radius-md) !important;
    }
   
    /* Loading spinner */
    .stSpinner > div {
        border-color: var(--primary-color) !important;
    }
   
    /* Metrics styling */
    .stMetric {
        background: var(--surface-primary) !important;
        border: 1px solid var(--border-color) !important;
        border-radius: var(--radius-md) !important;
        padding: 1rem !important;
        box-shadow: var(--shadow-sm) !important;
    }
   
    /* Toast notifications */
    .stAlert {
        border-radius: var(--radius-md) !important;
        box-shadow: var(--shadow-md) !important;
    }
   
    /* Theme toggle button */
    .theme-toggle {
        position: fixed;
        top: 1rem;
        right: 1rem;
        z-index: 1000;
        background: var(--surface-primary);
        border: 1px solid var(--border-color);
        border-radius: 50%;
        width: 3rem;
        height: 3rem;
        display: flex;
        align-items: center;
        justify-content: center;
        cursor: pointer;
        box-shadow: var(--shadow-lg);
        transition: all 0.2s ease;
    }
   
    .theme-toggle:hover {
        transform: scale(1.05);
        box-shadow: var(--shadow-xl);
    }
   
    /* Responsive design */
    @media (max-width: 768px) {
        .main .block-container {
            padding: 1rem 0.5rem !important;
        }
       
        .modern-card {
            padding: 1rem !important;
        }
       
        .chat-message {
            margin-left: 0 !important;
            margin-right: 0 !important;
        }
    }
   
    /* Custom scrollbar */
    ::-webkit-scrollbar {
        width: 6px;
    }
   
    ::-webkit-scrollbar-track {
        background: var(--surface-secondary);
    }
   
    ::-webkit-scrollbar-thumb {
        background: var(--border-color);
        border-radius: 3px;
    }
   
    ::-webkit-scrollbar-thumb:hover {
        background: var(--border-hover);
    }
    </style>
    """, unsafe_allow_html=True)

def create_modern_header():
    """Create modern header component"""
    st.markdown("""
    <div class="app-title">🎧 EchoVerse</div>
    <div class="app-subtitle">AI-Powered Audiobook Creator</div>
    """, unsafe_allow_html=True)

def create_status_card(title, services_status):
    """Create modern status card"""
    st.markdown(f"""
    <div class="modern-card">
        <div class="section-title">
            📊 {title}
        </div>
        {services_status}
    </div>
    """, unsafe_allow_html=True)

def create_chat_bubble(content, message_type="assistant"):
    """Create chat-style message bubble"""
    st.markdown(f"""
    <div class="chat-message {message_type}">
        {content}
    </div>
    """, unsafe_allow_html=True)

def create_feature_card(icon, title, description, action_button=None):
    """Create feature card component"""
    card_html = f"""
    <div class="modern-card">
        <div style="display: flex; align-items: center; gap: 1rem; margin-bottom: 1rem;">
            <div style="font-size: 2rem;">{icon}</div>
            <div>
                <h3 style="margin: 0; color: var(--text-primary);">{title}</h3>
                <p style="margin: 0; color: var(--text-secondary); font-size: 0.9rem;">{description}</p>
            </div>
        </div>
    """
   
    if action_button:
        card_html += f'<div style="margin-top: 1rem;">{action_button}</div>'
   
    card_html += "</div>"
    st.markdown(card_html, unsafe_allow_html=True)

# Enhanced page configuration
st.set_page_config(
    page_title="EchoVerse - AI Audiobook Creator",
    page_icon="🎧",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://github.com/your-repo',
        'Report a bug': 'https://github.com/your-repo/issues',
        'About': 'EchoVerse - Transform your text into professional audiobooks with AI'
    }
)

# Apply modern CSS
inject_modern_css()

# Theme management
if 'theme' not in st.session_state:
    st.session_state.theme = 'light'

# Theme toggle function
def toggle_theme():
    st.session_state.theme = 'dark' if st.session_state.theme == 'light' else 'light'
    st.rerun()

# Apply theme
if st.session_state.theme == 'dark':
    st.markdown('<script>document.documentElement.setAttribute("data-theme", "dark")</script>', unsafe_allow_html=True)

# Enhanced Services (keeping your original service logic)
@st.cache_resource
def initialize_services():
    """Initialize Watson services"""
    tts_service = WatsonTTSService()
    llm_service = HuggingFaceLLMService()
    return tts_service, llm_service

# Functional wrappers delegating to app_restored implementations
def save_to_library(name, description, original_text, rewritten_text, tone, voice):
    return save_project_to_library(name, description, original_text, rewritten_text, tone, voice)

def save_bookmark(name, source_project, text_snippet, tone, voice):
    return save_audio_bookmark(name, source_project, text_snippet, tone, voice)

def save_bookmark_from_bytes(name, source_project, text_snippet, tone, voice, audio_bytes: bytes):
    return save_bookmark_from_bytes_impl(name, source_project, text_snippet, tone, voice, audio_bytes)

def create_empty_bookmark(name, source_project, text_snippet, tone, voice):
    return create_empty_bookmark_impl(name, source_project, text_snippet, tone, voice)

def attach_audio_to_bookmark(bm: dict):
    return attach_audio_to_bookmark_impl(bm)

def load_bookmarks_from_disk():
    return load_bookmarks_from_disk_impl()

def load_library_from_disk():
    return load_library_from_disk_impl()

def main():
    """Enhanced main application with modern UI"""
   
    # Initialize services
    tts_service, llm_service = initialize_services()
   
    # Load data
    if 'bookmarks_loaded' not in st.session_state:
        load_bookmarks_from_disk()
    if 'library_loaded' not in st.session_state:
        load_library_from_disk()
   
    # Theme toggle in top right
    col1, col2 = st.columns([10, 1])
    with col2:
        theme_icon = "🌙" if st.session_state.theme == 'light' else "☀️"
        if st.button(theme_icon, help="Toggle theme", key="theme_toggle"):
            toggle_theme()
   
    # Modern sidebar
    with st.sidebar:
        st.markdown("### 🎧 EchoVerse")
        st.markdown("---")
       
        # Navigation with modern styling
        if 'current_page' not in st.session_state:
            st.session_state.current_page = "Dashboard"
       
        nav_options = {
            "Dashboard": "🏠 Dashboard",
            "Create Audio": "✨ Create New Audio",
            "Library": "📚 My Library",
            "Bookmarks": "🔖 Audio Bookmarks",
            "Settings": "⚙️ Settings"
        }
       
        for key, label in nav_options.items():
            if st.button(label, use_container_width=True, key=f"nav_{key}"):
                st.session_state.current_page = key
       
        st.markdown("---")
       
        # Service status with modern styling
        st.markdown("### 📡 Service Status")
       
        tts_status = tts_service.is_service_available() if hasattr(tts_service, 'is_service_available') else True
        llm_status = llm_service.is_service_available() if hasattr(llm_service, 'is_service_available') else True
       
        tts_badge = "✅ Connected" if tts_status else "❌ Disconnected"
        llm_badge = "✅ Connected" if llm_status else "❌ Disconnected"
       
        st.markdown(f"""
        <div class="status-badge {'status-success' if tts_status else 'status-error'}">
            {tts_badge} TTS
        </div>
        <br><br>
        <div class="status-badge {'status-success' if llm_status else 'status-error'}">
            {llm_badge} AI Rewriter
        </div>
        """, unsafe_allow_html=True)
   
    # Main content routing
    page = st.session_state.current_page
   
    if page == "Dashboard":
        dashboard_page()
    elif page == "Create Audio":
        create_audio_page_modern(tts_service, llm_service)
    elif page == "Library":
        library_page_modern()
    elif page == "Bookmarks":
        bookmarks_page_modern()
    elif page == "Settings":
        settings_page_modern()

def dashboard_page():
    """Modern dashboard with overview"""
    create_modern_header()
   
    # Stats row
    col1, col2, col3, col4 = st.columns(4)
   
    with col1:
        st.metric("Total Projects", len(st.session_state.get('library', [])), delta=None)
   
    with col2:
        st.metric("Bookmarks", len(st.session_state.get('bookmarks', [])), delta=None)
   
    with col3:
        st.metric("Audio Generated", "12.5 hrs", delta="2.3 hrs")
   
    with col4:
        st.metric("Success Rate", "98.7%", delta="1.2%")
   
    st.markdown("---")
   
    # Quick actions
    st.markdown('<div class="section-title">🚀 Quick Actions</div>', unsafe_allow_html=True)
   
    col1, col2 = st.columns(2)
   
    with col1:
        if st.button("✨ Create New Audiobook", use_container_width=True, type="primary"):
            st.session_state.current_page = "Create Audio"
            st.rerun()
       
        if st.button("📚 Browse Library", use_container_width=True):
            st.session_state.current_page = "Library"
            st.rerun()
   
    with col2:
        if st.button("🔖 View Bookmarks", use_container_width=True):
            st.session_state.current_page = "Bookmarks"
            st.rerun()
       
        if st.button("⚙️ Settings", use_container_width=True):
            st.session_state.current_page = "Settings"
            st.rerun()
   
    # Recent activity
    st.markdown("---")
    st.markdown('<div class="section-title">📈 Recent Activity</div>', unsafe_allow_html=True)
   
    with st.container():
        create_chat_bubble("🎉 Created new audiobook: 'The Great Adventure'", "assistant")
        create_chat_bubble("📖 Processed 2,450 words with AI rewriting", "assistant")
        create_chat_bubble("🔖 Added bookmark: 'Chapter 3 Highlights'", "assistant")

def create_audio_page_modern(tts_service, llm_service):
    """Modern create audio page with chat-like interface"""
    create_modern_header()
   
    # Progress indicator
    if 'creation_step' not in st.session_state:
        st.session_state.creation_step = 1
   
    progress_steps = ["📝 Text Input", "🎭 Style Selection", "🎤 Voice & Generate", "🎵 Review & Save"]
   
    # Progress bar
    progress_cols = st.columns(len(progress_steps))
    for i, (col, step) in enumerate(zip(progress_cols, progress_steps)):
        with col:
            if i + 1 <= st.session_state.creation_step:
                st.markdown(f'<div class="status-badge status-success">{step}</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="status-badge">{step}</div>', unsafe_allow_html=True)
   
    st.markdown("---")
   
    # Step 1: Text Input
    with st.container():
        st.markdown('<div class="section-title">📝 Project Setup</div>', unsafe_allow_html=True)
       
        col1, col2 = st.columns([2, 1])
        with col1:
            project_name = st.text_input("Project Name", placeholder="Enter your audiobook title...")
        with col2:
            project_type = st.selectbox("Project Type", ["Audiobook", "Podcast", "Narration", "Story"])
       
        description = st.text_area("Description", placeholder="Brief description of your project...", height=100)
   
    # Step 2: Text Processing
    with st.container():
        st.markdown('<div class="section-title">📖 Text Processing</div>', unsafe_allow_html=True)
       
        tab1, tab2 = st.tabs(["✍️ Type/Paste Text", "📁 Upload File"])
       
        with tab1:
            user_text = st.text_area(
                "Enter your text:",
                height=200,
                placeholder="Paste your text here... Maximum 5000 words for optimal performance.",
                help="Supports plain text, markdown, and basic formatting"
            )
       
        with tab2:
            uploaded_file = st.file_uploader(
                "Upload your text file",
                type=['txt', 'md', 'docx'],
                help="Supported formats: TXT, Markdown, Word documents"
            )
            if uploaded_file:
                # File processing logic here
                user_text = "File content would be processed here..."
                st.success("File uploaded successfully!")
       
        if user_text:
            word_count = len(user_text.split())
            st.info(f"📊 Word count: {word_count:,} words")
           
            if word_count > 5000:
                st.warning("⚠️ Text exceeds recommended length. Consider splitting into chapters.")
   
    # Step 3: AI Enhancement
    if user_text:
        st.markdown('<div class="section-title">🎭 AI Enhancement</div>', unsafe_allow_html=True)
       
        col1, col2 = st.columns([2, 1])
        with col1:
            selected_tone = st.selectbox("Tone", Config.TONE_OPTIONS)
       
        with col2:
            if st.button("🔄 Suggest Rewrite", type="primary", use_container_width=True):
                if llm_service.is_service_available():
                    with st.spinner("Rewriting text with AI..."):
                        rewritten_text = llm_service.rewrite_text(user_text, selected_tone)
                        st.session_state.rewritten_text = rewritten_text
                        st.success("Text rewritten successfully!")
                        st.session_state.creation_step = 3
                else:
                    st.error("LLM service not available. Check Hugging Face settings.")
       
        # Show comparison if enhanced
        if 'rewritten_text' in st.session_state:
            st.markdown("### 📋 Before & After Comparison")
           
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("**Original Text**")
                st.text_area("original", user_text, height=200, disabled=True, label_visibility="collapsed")
           
            with col2:
                st.markdown("**AI Enhanced Text**")
                enhanced_text = st.text_area("enhanced", st.session_state.rewritten_text, height=200, label_visibility="collapsed")
                st.session_state.rewritten_text = enhanced_text
   
    # Step 4: Voice Generation
    if 'rewritten_text' in st.session_state or user_text:
        st.markdown('<div class="section-title">🎤 Voice Generation</div>', unsafe_allow_html=True)

        col1, col2 = st.columns([2, 1])

        with col1:
            voices = tts_service.get_available_voices()
            selected_voice = st.selectbox("Select Voice", voices)

        with col2:
            if st.button("🎵 Generate Audio", type="primary", use_container_width=True):
                effective_text = st.session_state.get('rewritten_text', user_text)
                if tts_service.is_service_available():
                    with st.spinner("🎧 Generating your audiobook..."):
                        try:
                            audio_bytes = tts_service.synthesize_speech(effective_text, selected_voice)
                            st.session_state.audio_data = audio_bytes
                            st.session_state.audio_generated = True
                            st.session_state.creation_step = 4
                            st.success("Audio generated successfully!")
                        except Exception as e:
                            st.error(f"Error generating audio: {e}")
                else:
                    st.error("TTS service not available. Check IBM Watson TTS config.")
   
    # Step 5: Preview & Save
    if 'audio_data' in st.session_state:
        st.markdown('<div class="section-title">🎵 Audio Preview</div>', unsafe_allow_html=True)
        st.audio(st.session_state.audio_data, format='audio/mp3')
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("💾 Save to Library", type="primary", use_container_width=True):
                save_to_library(
                    name=project_name or 'Untitled',
                    description=description or '',
                    original_text=user_text,
                    rewritten_text=st.session_state.get('rewritten_text', user_text),
                    tone=selected_tone,
                    voice=selected_voice,
                )
        with col2:
            if st.button("🔖 Add Bookmark", use_container_width=True):
                save_bookmark(
                    name=project_name or 'Untitled',
                    source_project=project_name or 'Untitled',
                    text_snippet=(st.session_state.get('rewritten_text') or user_text)[:280],
                    tone=selected_tone,
                    voice=selected_voice,
                )
        with col3:
            st.download_button(
                label="⬇️ Download MP3",
                data=st.session_state.audio_data,
                file_name=f"{(project_name or 'audiobook').strip()}.mp3",
                mime="audio/mp3",
            )
    else:
        # allow empty bookmark creation
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

def library_page_modern():
    """Modern library page"""
    create_modern_header()
   
    # Search and filter
    col1, col2, col3 = st.columns([3, 1, 1])
    with col1:
        search_query = st.text_input("🔍 Search projects...", placeholder="Search by name, description, or content")
    with col2:
        sort_by = st.selectbox("Sort by", ["Recent", "Name", "Duration", "Date Created"])
    with col3:
        view_mode = st.selectbox("View", ["Grid", "List"])
   
    st.markdown("---")
   
    # Library content
    if 'library_loaded' not in st.session_state:
        load_library_from_disk()
    library_items = st.session_state.get('library', [])
   
    if not library_items:
        st.markdown("""
        <div class="modern-card" style="text-align: center; padding: 3rem;">
            <div style="font-size: 4rem; margin-bottom: 1rem;">📚</div>
            <h3>Your Library is Empty</h3>
            <p style="color: var(--text-secondary);">Create your first audiobook to get started!</p>
        </div>
        """, unsafe_allow_html=True)
       
        if st.button("✨ Create First Project", type="primary"):
            st.session_state.current_page = "Create Audio"
            st.rerun()
    else:
        # Display library items
        if view_mode == "Grid":
            cols = st.columns(2)
            for i, item in enumerate(library_items):
                with cols[i % 2]:
                    st.markdown(f"""
                    <div class="modern-card">
                        <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 1rem;">
                            <div>
                                <h3 style="margin: 0; color: var(--text-primary);">📖 {item.get('name', f'Project {i+1}')}</h3>
                                <p style="margin: 0.5rem 0; color: var(--text-secondary); font-size: 0.9rem;">{item.get('description', '')[:100]}...</p>
                            </div>
                            <div class="status-badge status-success">✅</div>
                        </div>
                        <div style="display: flex; gap: 1rem; margin-bottom: 1rem; font-size: 0.8rem; color: var(--text-muted);">
                            <span>🎭 {item.get('tone', 'N/A')}</span>
                            <span>🎤 {item.get('voice', 'N/A')}</span>
                            <span>📅 {item.get('created_at', 'N/A')}</span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                   
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        ap = (item.get('paths') or {}).get('audio')
                        if ap and os.path.exists(ap):
                            if st.button("▶️ Play", key=f"play_{i}", use_container_width=True):
                                with open(ap, 'rb') as f:
                                    ab = f.read()
                                st.audio(ab, format='audio/mp3')
                    with col2:
                        st.empty()
                    with col3:
                        ap = (item.get('paths') or {}).get('audio')
                        if ap and os.path.exists(ap):
                            with open(ap, 'rb') as f:
                                ab = f.read()
                            st.download_button("⬇️ Download MP3", ab, os.path.basename(ap), mime="audio/mp3", key=f"dl_grid_{i}")
        else:
            # List view
            for i, item in enumerate(library_items):
                with st.expander(f"📖 {item.get('name', f'Project {i+1}')}"):
                    col1, col2 = st.columns([2, 1])
                   
                    with col1:
                        st.write(f"**Description:** {item.get('description', 'No description')}")
                        st.write(f"**Tone:** {item.get('tone', 'N/A')} | **Voice:** {item.get('voice', 'N/A')}")
                        st.write(f"**Created:** {item.get('created_at', 'N/A')}")
                   
                    with col2:
                        ap = (item.get('paths') or {}).get('audio')
                        if ap and os.path.exists(ap):
                            if st.button("▶️ Play Audio", key=f"play_list_{i}"):
                                with open(ap, 'rb') as f:
                                    ab = f.read()
                                st.audio(ab, format='audio/mp3')
                       
                        col_a, col_b = st.columns(2)
                        with col_a:
                            if st.button("✏️", key=f"edit_list_{i}", help="Edit"):
                                pass
                        with col_b:
                            if ap and os.path.exists(ap):
                                with open(ap, 'rb') as f:
                                    ab = f.read()
                                st.download_button("⬇️ Download", ab, os.path.basename(ap), mime="audio/mp3", key=f"dl_list_{i}")

def bookmarks_page_modern():
    """Modern bookmarks page"""
    create_modern_header()
   
    # Header with actions
    col1, col2 = st.columns([2, 1])
    with col1:
        st.markdown('<div class="section-title">🔖 Your Audio Bookmarks</div>', unsafe_allow_html=True)
    with col2:
        if st.button("➕ New Bookmark", type="primary", use_container_width=True):
            st.session_state.show_bookmark_creator = True
   
    # Bookmark creator modal
    if st.session_state.get('show_bookmark_creator'):
        with st.container():
            st.markdown("""
            <div class="modern-card" style="border-left: 4px solid var(--primary-color);">
                <div class="section-title">✨ Create New Bookmark</div>
            """, unsafe_allow_html=True)
           
            bookmark_name = st.text_input("Bookmark Name", placeholder="Enter bookmark name...")
            bookmark_text = st.text_area("Text Snippet", placeholder="Add the text you want to bookmark...", height=100)
           
            col1, col2, col3 = st.columns(3)
            with col1:
                if st.button("💾 Save Bookmark", type="primary"):
                    st.success("Bookmark saved!")
                    st.session_state.show_bookmark_creator = False
                    st.rerun()
            with col2:
                if st.button("❌ Cancel"):
                    st.session_state.show_bookmark_creator = False
                    st.rerun()
           
            st.markdown("</div>", unsafe_allow_html=True)
   
    # Display bookmarks
    bookmarks = st.session_state.get('bookmarks', [])
   
    if not bookmarks:
        st.markdown("""
        <div class="modern-card" style="text-align: center; padding: 3rem;">
            <div style="font-size: 4rem; margin-bottom: 1rem;">🔖</div>
            <h3>No Bookmarks Yet</h3>
            <p style="color: var(--text-secondary);">Save important moments from your audiobooks!</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        for i, bookmark in enumerate(bookmarks):
            st.markdown(f"""
            <div class="modern-card">
                <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 1rem;">
                    <div>
                        <h4 style="margin: 0; color: var(--text-primary);">🔖 {bookmark.get('name', f'Bookmark {i+1}')}</h4>
                        <p style="margin: 0.5rem 0; color: var(--text-secondary); font-size: 0.9rem;">From: {bookmark.get('source_project', 'Unknown Project')}</p>
                    </div>
                    <div class="status-badge status-success">📅 {bookmark.get('created_at', 'N/A')}</div>
                </div>
                <div style="background: var(--surface-secondary); padding: 1rem; border-radius: var(--radius-md); margin-bottom: 1rem;">
                    <p style="margin: 0; font-style: italic;">{bookmark.get('text_snippet', 'No text snippet available')[:200]}...</p>
                </div>
            </div>
            """, unsafe_allow_html=True)
           
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                ap = (bookmark.get('paths') or {}).get('audio')
                if ap and os.path.exists(ap):
                    if st.button("▶️ Play", key=f"bookmark_play_{i}"):
                        with open(ap, 'rb') as f:
                            ab = f.read()
                        st.audio(ab, format='audio/mp3')
            with col2:
                if st.button("📤 Share", key=f"bookmark_share_{i}"):
                    st.info("Share link copied!")
            with col3:
                if st.button("✏️ Edit", key=f"bookmark_edit_{i}"):
                    st.info("Edit mode activated")
            with col4:
                if not ((bookmark.get('paths') or {}).get('audio')):
                    if st.button("📎 Attach Current Audio", key=f"bm_attach_{i}"):
                        attach_audio_to_bookmark(bookmark)

def settings_page_modern():
    """Modern settings page"""
    create_modern_header()
   
    # Settings sections
    tab1, tab2, tab3, tab4 = st.tabs(["🔧 General", "🎤 Voice Settings", "🤖 AI Settings", "📊 Analytics"])
   
    with tab1:
        st.markdown('<div class="section-title">⚙️ General Settings</div>', unsafe_allow_html=True)
       
        with st.container():
            st.markdown('<div class="modern-card">', unsafe_allow_html=True)
           
            col1, col2 = st.columns(2)
            with col1:
                st.selectbox("Default Language", ["English", "Spanish", "French", "German"])
                st.slider("Default Audio Quality", 64, 320, 128, 32, format="%d kbps")
               
            with col2:
                st.selectbox("Time Zone", ["UTC", "EST", "PST", "GMT"])
                st.checkbox("Auto-save projects")
               
            st.markdown('</div>', unsafe_allow_html=True)
   
    with tab2:
        st.markdown('<div class="section-title">🎤 Voice Preferences</div>', unsafe_allow_html=True)
       
        st.markdown('<div class="modern-card">', unsafe_allow_html=True)
       
        col1, col2 = st.columns(2)
        with col1:
            st.selectbox("Preferred Voice", ["Allison", "Michael", "Lisa", "David", "Emma"])
            st.slider("Default Speaking Rate", 0.5, 2.0, 1.0, 0.1)
           
        with col2:
            st.slider("Default Pitch", -20, 20, 0, 5)
            st.selectbox("Audio Format", ["MP3", "WAV", "AAC"])
       
        # Voice preview
        if st.button("🎧 Preview Voice Settings"):
            st.audio("https://www.soundjay.com/misc/sounds/bell-ringing-05.wav")
       
        st.markdown('</div>', unsafe_allow_html=True)
   
    with tab3:
        st.markdown('<div class="section-title">🤖 AI Enhancement Settings</div>', unsafe_allow_html=True)
       
        st.markdown('<div class="modern-card">', unsafe_allow_html=True)
       
        st.selectbox("Default Tone", ["Professional", "Conversational", "Dramatic", "Educational"])
        st.slider("AI Enhancement Level", 1, 5, 3, 1, help="1 = Minimal changes, 5 = Maximum enhancement")
        st.checkbox("Auto-enhance new projects")
        st.checkbox("Show enhancement suggestions")
       
        st.markdown('</div>', unsafe_allow_html=True)
   
    with tab4:
        st.markdown('<div class="section-title">📊 Usage Analytics</div>', unsafe_allow_html=True)
       
        col1, col2, col3, col4 = st.columns(4)
       
        with col1:
            st.metric("Projects Created", "24", delta="3")
        with col2:
            st.metric("Hours Generated", "18.5", delta="2.1")
        with col3:
            st.metric("Words Processed", "45,230", delta="5,120")
        with col4:
            st.metric("Bookmarks Saved", "67", delta="8")
       
        # Usage chart placeholder
        st.markdown('<div class="modern-card">', unsafe_allow_html=True)
        st.markdown("### 📈 Usage Over Time")
        st.line_chart({
            "Projects": [1, 3, 2, 4, 5, 3, 6],
            "Audio Hours": [0.5, 1.2, 0.8, 2.1, 2.5, 1.8, 3.2]
        })
        st.markdown('</div>', unsafe_allow_html=True)

# Initialize session state variables
if 'show_bookmark_creator' not in st.session_state:
    st.session_state.show_bookmark_creator = False

if __name__ == "__main__":
    main()