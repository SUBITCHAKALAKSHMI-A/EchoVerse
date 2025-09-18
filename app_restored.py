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

# Background image helpers

def _encode_image_base64(img_path: str) -> str:
    try:
        with open(img_path, "rb") as f:
            return base64.b64encode(f.read()).decode("utf-8")
    except Exception:
        return ""


def _detect_mime_type(img_path: str) -> str:
    ext = os.path.splitext(img_path)[1].lower()
    return {
        ".png": "image/png",
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".webp": "image/webp",
        ".gif": "image/gif",
    }.get(ext, "image/jpeg")


def build_background_css() -> str:
    here = os.path.dirname(__file__)
    candidates = [
        os.path.join(here, "background.jpg"),
        os.path.join(here, "assets", "background1.jpg"),
        os.path.join(here, "background.png"),
        os.path.join(here, "assets", "background.png"),
    ]
    for p in candidates:
        if os.path.exists(p):
            b64 = _encode_image_base64(p)
            if not b64:
                continue
            mime = _detect_mime_type(p)
            return (
                f"<style>"
                f"html, body, [data-testid='stAppViewContainer'] {{"
                f"background-image: url('data:{mime};base64,{b64}') !important;"
                f"background-size: cover !important;"
                f"background-attachment: fixed !important;"
                f"background-position: center center !important;"
                f"}}"
                f"[data-testid='stAppViewContainer'] .main .block-container {{"
                f"background: rgba(255,255,255,0.80);"
                f"border-radius: 12px;"
                f"padding: 1rem 1.25rem;"
                f"}}"
                f"</style>"
            )
    return ""

# Page configuration (only when running this script directly)
def _configure_page():
    st.set_page_config(
        page_title="EchoVerse - AI Audiobook Creator",
        page_icon="🎧",
        layout="wide",
        initial_sidebar_state="expanded"
    )

# Custom CSS for styling

def apply_theme(is_dark: bool):
    """Inject CSS variables for light/dark themes and base styles that consume them, without f-string braces issues."""
    if is_dark:
        # Blue + Black combo
        vars_css = """
        :root {
            --bg: #0a0f1a;
            --text: #e6edf3;
            --muted: #9aa4b2;
            --card-bg: #0f1726;
            --card-shadow: rgba(0,0,0,0.35);
            --border: #1f2a44;
            --panel: #0b1324;
            --accent: #3b82f6; /* blue */
            --success-bg: #0f3321;
            --success-text: #77e0a1;
            --error-bg: #3a1116;
            --error-text: #f3a4a8;
        }
        """
    else:
        vars_css = """
        :root {
            --bg: #f6f8ff;
            --text: #0f172a;
            --muted: #64748b;
            --card-bg: #ffffff;
            --card-shadow: rgba(0,0,0,0.08);
            --border: #e5e7eb;
            --panel: #ffffff;
            --accent: #2563eb; /* blue */
            --success-bg: #d1fadf;
            --success-text: #166534;
            --error-bg: #fee2e2;
            --error-text: #991b1b;
        }
        """

    other_css = """
        /* Base */
        html, body, [data-testid="stAppViewContainer"] { background: var(--bg) !important; color: var(--text) !important; }
        [data-testid="stSidebar"] {
            background: var(--panel) !important;
            color: var(--text) !important;
            border-right: 1px solid var(--border);
            padding: 12px 14px !important; /* normalize padding for straight alignment */
            text-align: left !important; /* ensure left alignment */
        }
        [data-testid="stSidebar"] .block-container { padding: 0 !important; }
        /* Typography */
        .main-header {
            font-size: 2.5rem;
            font-weight: bold;
            color: var(--text);
            text-align: center;
            margin-bottom: 2rem;
        }
        .section-header {
            font-size: 1.5rem;
            font-weight: 600;
            color: var(--text);
            margin-top: 2rem;
            margin-bottom: 1rem;
        }
        /* Cards */
        .card {
            background: var(--card-bg);
            padding: 1.5rem;
            border-radius: 10px;
            box-shadow: 0 2px 8px var(--card-shadow);
            margin-bottom: 1rem;
            border: 1px solid var(--border);
        }
        .text-comparison { display: flex; gap: 1rem; }
        .text-column {
            flex: 1;
            padding: 1rem;
            border: 1px solid var(--border);
            border-radius: 8px;
            background: var(--card-bg);
            color: var(--text);
        }
        .sidebar-section { margin-bottom: 1.25rem; }
        .status-indicator {
            padding: 0.25rem 0.75rem;
            border-radius: 20px;
            font-size: 0.8rem;
            font-weight: 500;
        }
        .status-success { background: var(--success-bg); color: var(--success-text); }
        .status-error { background: var(--error-bg); color: var(--error-text); }
        /* Typography */
        [data-testid="stMarkdownContainer"], [data-testid="stAppViewContainer"], [data-testid="stSidebar"], [data-testid="stSidebar"] *, h1, h2, h3, h4, h5, h6, p, span, li, label { color: var(--text) !important; }
        a { color: var(--accent) !important; }
        /* Inputs */
        textarea, input, select { color: var(--text) !important; background: var(--card-bg) !important; border-color: var(--border) !important; }
        textarea::placeholder, input::placeholder { color: var(--muted) !important; }
        [data-testid="stTextArea"] textarea, [data-testid="stTextInput"] input, [data-testid="stSelectbox"] div, [data-testid="stFileUploader"] div, [data-baseweb="select"] div { color: var(--text) !important; background: var(--card-bg) !important; }
        [data-baseweb="select"] input { color: var(--text) !important; }
        [role="radiogroup"] label, [data-testid="stCheckbox"] label { color: var(--text) !important; }
        /* Ensure inputs in sidebar are full width and aligned */
        [data-testid="stSidebar"] [data-testid="stTextArea"],
        [data-testid="stSidebar"] [data-testid="stTextInput"],
        [data-testid="stSidebar"] [data-testid="stSelectbox"],
        [data-testid="stSidebar"] [data-testid="stFileUploader"] {
            width: 100% !important;
        }

        /* Buttons */
        .stButton button, .stDownloadButton button { color: var(--text) !important; background: var(--card-bg) !important; border: 1px solid var(--border) !important; }
        .stButton button:hover, .stDownloadButton button:hover { filter: brightness(1.05); }
        .stButton button[kind="primary"], .stDownloadButton button[kind="primary"] { background: var(--accent) !important; color: #ffffff !important; border-color: transparent !important; }
        /* Sidebar buttons: full width and left-aligned for straight edges */
        [data-testid="stSidebar"] .stButton > button,
        [data-testid="stSidebar"] .stDownloadButton > button {
            width: 100% !important;
            justify-content: flex-start !important;
            text-align: left !important;
            border-radius: 8px !important;
            padding: 0.6rem 0.9rem !important;
        }
        [data-testid="stSidebar"] .stButton { margin-bottom: 8px !important; }

        /* Responsive tweaks: keep labels readable and alignment intact */
        @media (max-width: 1100px) {
            [data-testid="stSidebar"] { padding: 10px 12px !important; }
        }

        /* Floating hamburger at top-left */
        .ev-hamburger {
            position: fixed;
            top: 12px;
            left: 12px;
            z-index: 1002;
            background: var(--card-bg);
            color: var(--text) !important;
            border: 1px solid var(--border);
            border-radius: 10px;
            padding: 8px 10px;
            text-decoration: none !important;
            font-weight: 700;
            box-shadow: 0 2px 10px var(--card-shadow);
        }
    """

    # Inject background image CSS if present
    bg_css = build_background_css()
    st.markdown("<style>" + vars_css + other_css + "</style>" + (bg_css or ""), unsafe_allow_html=True)


# Theme initialization and application (only when running this script directly)
def _init_theme():
    if 'theme' not in st.session_state:
        st.session_state.theme = 'Light'
    apply_theme(st.session_state.theme == 'Dark')


# Initialize services
@st.cache_resource
def initialize_services():
    """Initialize Watson services"""
    tts_service = WatsonTTSService()
    llm_service = HuggingFaceLLMService()
    return tts_service, llm_service


def save_to_library(name, description, original_text, rewritten_text, tone, voice):
    """Save audio project to library"""
    if 'library' not in st.session_state:
        st.session_state.library = []

    # Ensure library directory exists
    os.makedirs(Config.LIBRARY_DIR, exist_ok=True)

    def _sanitize(text: str) -> str:
        safe = "".join(c for c in (text or "untitled") if c.isalnum() or c in (' ', '-', '_'))
        safe = " ".join(safe.split())  # collapse spaces
        return safe.strip().replace(' ', '_')[:80] or 'project'

    project_dir_name = _sanitize(name)
    project_dir = os.path.join(Config.LIBRARY_DIR, project_dir_name)
    # If project dir exists, create unique suffix
    suffix = 1
    unique_project_dir = project_dir
    while os.path.exists(unique_project_dir):
        suffix += 1
        unique_project_dir = f"{project_dir}_{suffix}"
    project_dir = unique_project_dir
    os.makedirs(project_dir, exist_ok=True)

    # Paths
    original_path = os.path.join(project_dir, 'original.txt')
    rewritten_path = os.path.join(project_dir, 'rewritten.txt')
    audio_path = os.path.join(project_dir, 'audio.mp3')
    meta_path = os.path.join(project_dir, 'metadata.json')

    # Write files
    try:
        with open(original_path, 'w', encoding='utf-8') as f:
            f.write(original_text or '')
        with open(rewritten_path, 'w', encoding='utf-8') as f:
            f.write(rewritten_text or '')
        # Write audio if present
        audio_bytes = st.session_state.get('audio_data')
        if audio_bytes:
            try:
                # audio_bytes may be bytes or BytesIO
                if isinstance(audio_bytes, io.BytesIO):
                    data = audio_bytes.getvalue()
                else:
                    data = audio_bytes
                with open(audio_path, 'wb') as f:
                    f.write(data)
            except Exception:
                audio_path = None
        else:
            audio_path = None

        metadata = {
            'name': name,
            'description': description,
            'tone': tone,
            'voice': voice,
            'created_at': str(st.session_state.get('current_time', 'Unknown')),
            'paths': {
                'original_text': original_path,
                'rewritten_text': rewritten_path,
                'audio': audio_path,
            },
        }
        with open(meta_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)

        # Store in-memory record with file paths
        project = {
            **metadata,
            'original_text': original_text,
            'rewritten_text': rewritten_text,
            'project_dir': project_dir,
        }
        st.session_state.library.append(project)

        msg = f"Project '{name}' saved to library at: {project_dir}"
        if not audio_path:
            msg += " (audio not available to save)"
        st.success(msg)
    except Exception as e:
        st.error(f"Failed to save project: {e}")


def save_bookmark_from_bytes(name: str, source_project: str, text_snippet: str, tone: str, voice: str, audio_bytes: bytes):
    """Core helper to save a bookmark given raw audio bytes."""
    os.makedirs(Config.BOOKMARKS_DIR, exist_ok=True)

    def _sanitize(text: str) -> str:
        safe = "".join(c for c in (text or "bookmark") if c.isalnum() or c in (' ', '-', '_'))
        safe = " ".join(safe.split())
        return safe.strip().replace(' ', '_')[:80] or 'bookmark'

    folder = _sanitize(name)
    base_dir = os.path.join(Config.BOOKMARKS_DIR, folder)
    suffix = 1
    unique_dir = base_dir
    while os.path.exists(unique_dir):
        suffix += 1
        unique_dir = f"{base_dir}_{suffix}"
    bdir = unique_dir
    os.makedirs(bdir, exist_ok=True)

    audio_path = os.path.join(bdir, 'audio.mp3')
    meta_path = os.path.join(bdir, 'metadata.json')

    with open(audio_path, 'wb') as f:
        f.write(audio_bytes)

    metadata = {
        'name': name,
        'source_project': source_project,
        'text_snippet': text_snippet,
        'tone': tone,
        'voice': voice,
        'created_at': datetime.now().isoformat(timespec='seconds'),
        'paths': {
            'audio': audio_path,
        }
    }
    with open(meta_path, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)

    if 'bookmarks' not in st.session_state:
        st.session_state.bookmarks = []
    st.session_state.bookmarks.append({**metadata, 'bookmark_dir': bdir})


def save_bookmark(name: str, source_project: str, text_snippet: str, tone: str, voice: str):
    """Save the current session audio as a bookmark (wraps save_bookmark_from_bytes)."""
    try:
        audio_obj = st.session_state.get('audio_data')
        if not audio_obj:
            st.warning("Generate audio first to save a bookmark.")
            return
        audio_bytes = audio_obj.getvalue() if isinstance(audio_obj, io.BytesIO) else audio_obj
        save_bookmark_from_bytes(name, source_project, text_snippet, tone, voice, audio_bytes)
        st.success(f"Bookmark '{name}' saved.")
    except Exception as e:
        st.error(f"Failed to save bookmark: {e}")


def create_empty_bookmark(name: str, source_project: str, text_snippet: str, tone: str, voice: str):
    """Create a bookmark folder and metadata without an audio file."""
    try:
        os.makedirs(Config.BOOKMARKS_DIR, exist_ok=True)

        def _sanitize(text: str) -> str:
            safe = "".join(c for c in (text or "bookmark") if c.isalnum() or c in (' ', '-', '_'))
            safe = " ".join(safe.split())
            return safe.strip().replace(' ', '_')[:80] or 'bookmark'

        folder = _sanitize(name)
        base_dir = os.path.join(Config.BOOKMARKS_DIR, folder)
        suffix = 1
        unique_dir = base_dir
        while os.path.exists(unique_dir):
            suffix += 1
            unique_dir = f"{base_dir}_{suffix}"
        bdir = unique_dir
        os.makedirs(bdir, exist_ok=True)

        meta_path = os.path.join(bdir, 'metadata.json')
        metadata = {
            'name': name,
            'source_project': source_project,
            'text_snippet': text_snippet,
            'tone': tone,
            'voice': voice,
            'created_at': datetime.now().isoformat(timespec='seconds'),
            'paths': {
                'audio': None,
            }
        }
        with open(meta_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)

        if 'bookmarks' not in st.session_state:
            st.session_state.bookmarks = []
        st.session_state.bookmarks.append({**metadata, 'bookmark_dir': bdir})
        st.success(f"Bookmark '{name}' created (no audio yet).")
    except Exception as e:
        st.error(f"Failed to create bookmark: {e}")


def attach_audio_to_bookmark(bm: dict):
    """Attach current session audio to an existing bookmark without audio."""
    try:
        audio_obj = st.session_state.get('audio_data')
        if not audio_obj:
            st.warning("Generate audio first, then attach.")
            return
        if not bm or not bm.get('bookmark_dir'):
            st.error("Invalid bookmark selection.")
            return
        audio_bytes = audio_obj.getvalue() if isinstance(audio_obj, io.BytesIO) else audio_obj
        bdir = bm['bookmark_dir']
        audio_path = os.path.join(bdir, 'audio.mp3')
        with open(audio_path, 'wb') as f:
            f.write(audio_bytes)
        # update metadata
        meta_path = os.path.join(bdir, 'metadata.json')
        try:
            with open(meta_path, 'r', encoding='utf-8') as f:
                meta = json.load(f)
        except Exception:
            meta = {}
        paths = meta.get('paths') or {}
        paths['audio'] = audio_path
        meta['paths'] = paths
        if 'name' not in meta:
            meta['name'] = bm.get('name', 'Bookmark')
        with open(meta_path, 'w', encoding='utf-8') as f:
            json.dump(meta, f, indent=2, ensure_ascii=False)
        _refresh_bookmarks_session()
        st.success("Audio attached to bookmark.")
    except Exception as e:
        st.error(f"Failed to attach audio: {e}")


def load_bookmarks_from_disk():
    """Scan BOOKMARKS_DIR for bookmarks and load into session_state.bookmarks."""
    try:
        os.makedirs(Config.BOOKMARKS_DIR, exist_ok=True)
        bookmarks = []
        for entry in sorted(os.listdir(Config.BOOKMARKS_DIR)):
            bdir = os.path.join(Config.BOOKMARKS_DIR, entry)
            if not os.path.isdir(bdir):
                continue
            meta_path = os.path.join(bdir, 'metadata.json')
            try:
                with open(meta_path, 'r', encoding='utf-8') as f:
                    meta = json.load(f)
                meta['bookmark_dir'] = bdir
                bookmarks.append(meta)
            except Exception:
                continue
        st.session_state.bookmarks = bookmarks
        st.session_state.bookmarks_loaded = True
    except Exception:
        st.session_state.bookmarks = []
        st.session_state.bookmarks_loaded = True


def display_bookmarks():
    """Render bookmarks list with playback and download."""
    bms = st.session_state.get('bookmarks') or []
    if not bms:
        st.info("No bookmarks saved yet. Create one from the Create New Audio page after generating audio.")
        return
    for i, bm in enumerate(bms):
        with st.expander(f"🔖 {bm.get('name', 'Bookmark')} - {bm.get('source_project', '')}"):
            st.write(f"**Source Project:** {bm.get('source_project','')}")
            st.write(f"**Tone:** {bm.get('tone','')}")
            st.write(f"**Voice:** {bm.get('voice','')}")
            st.write(f"**Created:** {bm.get('created_at','')}")
            if bm.get('bookmark_dir'):
                st.write(f"**Folder:** {bm['bookmark_dir']}")
            snippet = bm.get('text_snippet') or ''
            st.text_area("Snippet", snippet, height=100, key=f"bm_snip_{i}")

            # Playback and download
            audio_path = (bm.get('paths') or {}).get('audio')
            if audio_path and os.path.exists(audio_path):
                try:
                    with open(audio_path, 'rb') as f:
                        audio_bytes = f.read()
                    st.audio(audio_bytes, format='audio/mp3')
                    st.download_button(
                        label="⬇️ Download Bookmark MP3",
                        data=audio_bytes,
                        file_name=os.path.basename(audio_path),
                        mime="audio/mp3",
                        key=f"bm_dl_{i}"
                    )
                except Exception:
                    st.warning("Audio file could not be read.")
            else:
                # Allow attaching current audio if available
                ac_cols = st.columns([2, 1])
                with ac_cols[0]:
                    st.caption("No audio attached yet.")
                with ac_cols[1]:
                    attach_disabled = 'audio_data' not in st.session_state
                    if st.button("📎 Attach Current Audio", key=f"bm_attach_{i}", disabled=attach_disabled):
                        attach_audio_to_bookmark(bm)


def load_library_from_disk():
    """Scan LIBRARY_DIR and load saved projects into session_state.library."""
    try:
        os.makedirs(Config.LIBRARY_DIR, exist_ok=True)
        projects = []
        for entry in sorted(os.listdir(Config.LIBRARY_DIR)):
            pdir = os.path.join(Config.LIBRARY_DIR, entry)
            if not os.path.isdir(pdir):
                continue
            meta_path = os.path.join(pdir, 'metadata.json')
            original_path = os.path.join(pdir, 'original.txt')
            rewritten_path = os.path.join(pdir, 'rewritten.txt')
            try:
                meta = {}
                if os.path.exists(meta_path):
                    with open(meta_path, 'r', encoding='utf-8') as f:
                        meta = json.load(f)
                # read texts
                original_text = ''
                rewritten_text = ''
                if os.path.exists(original_path):
                    with open(original_path, 'r', encoding='utf-8') as f:
                        original_text = f.read()
                if os.path.exists(rewritten_path):
                    with open(rewritten_path, 'r', encoding='utf-8') as f:
                        rewritten_text = f.read()
                # Build project record
                paths = (meta.get('paths') or {}) if meta else {}
                # ensure audio path reflects folder
                ap = os.path.join(pdir, 'audio.mp3')
                if os.path.exists(ap):
                    paths['audio'] = ap
                project = {
                    'name': meta.get('name') if meta else entry,
                    'description': meta.get('description', ''),
                    'tone': meta.get('tone', ''),
                    'voice': meta.get('voice', ''),
                    'created_at': meta.get('created_at', ''),
                    'original_text': original_text,
                    'rewritten_text': rewritten_text or original_text,
                    'paths': paths,
                    'project_dir': pdir,
                }
                projects.append(project)
            except Exception:
                continue
        st.session_state.library = projects
        st.session_state.library_loaded = True
    except Exception:
        st.session_state.library = []
        st.session_state.library_loaded = True


def _sanitize_folder(text: str) -> str:
    safe = "".join(c for c in (text or "bookmark") if c.isalnum() or c in (' ', '-', '_'))
    safe = " ".join(safe.split())
    return safe.strip().replace(' ', '_')[:80] or 'bookmark'


def rename_bookmark(bm: dict, new_name: str):
    """Rename a bookmark (folder and metadata)."""
    try:
        if not bm or not bm.get('bookmark_dir'):
            st.error("Invalid bookmark to rename.")
            return
        old_dir = bm['bookmark_dir']
        parent = os.path.dirname(old_dir)
        target = os.path.join(parent, _sanitize_folder(new_name))
        # ensure uniqueness
        if os.path.abspath(target) == os.path.abspath(old_dir):
            # Only update metadata name
            _update_bookmark_name_only(old_dir, bm, new_name)
            return
        unique = target
        suffix = 1
        while os.path.exists(unique):
            suffix += 1
            unique = f"{target}_{suffix}"
        os.rename(old_dir, unique)
        _update_bookmark_paths_after_move(unique)
        _refresh_bookmarks_session()
        st.success("Bookmark renamed.")
    except Exception as e:
        st.error(f"Failed to rename: {e}")


def _update_bookmark_name_only(bdir: str, bm: dict, new_name: str):
    try:
        meta_path = os.path.join(bdir, 'metadata.json')
        with open(meta_path, 'r', encoding='utf-8') as f:
            meta = json.load(f)
        meta['name'] = new_name
        with open(meta_path, 'w', encoding='utf-8') as f:
            json.dump(meta, f, indent=2, ensure_ascii=False)
        _refresh_bookmarks_session()
        st.success("Bookmark renamed.")
    except Exception as e:
        st.error(f"Failed to update name: {e}")


def _update_bookmark_paths_after_move(new_dir: str):
    try:
        meta_path = os.path.join(new_dir, 'metadata.json')
        with open(meta_path, 'r', encoding='utf-8') as f:
            meta = json.load(f)
        # update any stored paths
        paths = meta.get('paths') or {}
        audio_path = os.path.join(new_dir, 'audio.mp3')
        if os.path.exists(audio_path):
            paths['audio'] = audio_path
        meta['paths'] = paths
        with open(meta_path, 'w', encoding='utf-8') as f:
            json.dump(meta, f, indent=2, ensure_ascii=False)
    except Exception:
        pass


def delete_bookmark(bm: dict):
    """Delete a bookmark folder and update session state."""
    try:
        if not bm or not bm.get('bookmark_dir'):
            st.error("Invalid bookmark to delete.")
            return
        bdir = bm['bookmark_dir']
        if os.path.isdir(bdir):
            shutil.rmtree(bdir)
        _refresh_bookmarks_session()
        st.success("Bookmark deleted.")
    except Exception as e:
        st.error(f"Failed to delete: {e}")


def _refresh_bookmarks_session():
    # Reload bookmarks from disk and reflect in session
    load_bookmarks_from_disk()


# ------ Library (Projects) management helpers ------
def _refresh_library_session():
    load_library_from_disk()


def rename_project(project: dict, new_name: str):
    """Rename a library project folder and update its metadata."""
    try:
        if not project or not project.get('project_dir'):
            st.error("Invalid project to rename.")
            return
        old_dir = project['project_dir']
        parent = os.path.dirname(old_dir)
        target = os.path.join(parent, _sanitize_folder(new_name))
        if os.path.abspath(target) == os.path.abspath(old_dir):
            _update_project_name_only(old_dir, project, new_name)
            return
        unique = target
        suffix = 1
        while os.path.exists(unique):
            suffix += 1
            unique = f"{target}_{suffix}"
        os.rename(old_dir, unique)
        _update_project_paths_after_move(unique)
        _refresh_library_session()
        st.success("Project renamed.")
    except Exception as e:
        st.error(f"Failed to rename project: {e}")


def delete_project(project: dict):
    """Delete a library project directory and refresh the library list."""
    try:
        if not project or not project.get('project_dir'):
            st.error("Invalid project to delete.")
            return
        pdir = project['project_dir']
        if os.path.isdir(pdir):
            shutil.rmtree(pdir)
        _refresh_library_session()
        st.success("Project deleted.")
    except Exception as e:
        st.error(f"Failed to delete project: {e}")


def _update_project_name_only(pdir: str, project: dict, new_name: str):
    try:
        meta_path = os.path.join(pdir, 'metadata.json')
        if os.path.exists(meta_path):
            with open(meta_path, 'r', encoding='utf-8') as f:
                meta = json.load(f)
        else:
            meta = {}
        meta['name'] = new_name
        with open(meta_path, 'w', encoding='utf-8') as f:
            json.dump(meta, f, indent=2, ensure_ascii=False)
        _refresh_library_session()
        st.success("Project renamed.")
    except Exception as e:
        st.error(f"Failed to update project name: {e}")


def _update_project_paths_after_move(new_dir: str):
    try:
        meta_path = os.path.join(new_dir, 'metadata.json')
        if os.path.exists(meta_path):
            with open(meta_path, 'r', encoding='utf-8') as f:
                meta = json.load(f)
        else:
            meta = {}
        paths = meta.get('paths') or {}
        # update canonical file paths
        op = os.path.join(new_dir, 'original.txt')
        rp = os.path.join(new_dir, 'rewritten.txt')
        ap = os.path.join(new_dir, 'audio.mp3')
        if os.path.exists(op):
            paths['original_text'] = op
        if os.path.exists(rp):
            paths['rewritten_text'] = rp
        if os.path.exists(ap):
            paths['audio'] = ap
        meta['paths'] = paths
        if 'name' not in meta:
            meta['name'] = os.path.basename(new_dir)
        with open(meta_path, 'w', encoding='utf-8') as f:
            json.dump(meta, f, indent=2, ensure_ascii=False)
    except Exception:
        pass
def display_library():
    """Display saved projects in library"""
    if 'library' not in st.session_state or not st.session_state.library:
        st.info("No projects saved yet. Create your first audiobook!")
        return

    for i, project in enumerate(st.session_state.library):
        with st.expander(f"📚 {project['name']}"):
            st.write(f"**Description:** {project['description']}")
            st.write(f"**Tone:** {project['tone']}")
            st.write(f"**Voice:** {project['voice']}")
            st.write(f"**Created:** {project['created_at']}")
            if project.get('project_dir'):
                st.write(f"**Folder:** {project['project_dir']}")

            col1, col2 = st.columns(2)
            with col1:
                st.text_area("Original Text", project['original_text'], height=100, key=f"orig_{i}")
            with col2:
                st.text_area("Rewritten Text", project['rewritten_text'], height=100, key=f"rewrite_{i}")

            # If audio file exists, allow playback and download
            audio_path = None
            if isinstance(project, dict):
                paths = project.get('paths') or {}
                audio_path = paths.get('audio')
            if audio_path and os.path.exists(audio_path):
                try:
                    with open(audio_path, 'rb') as f:
                        audio_bytes = f.read()
                    st.audio(audio_bytes, format='audio/mp3')
                    st.download_button(
                        label="⬇️ Download Saved MP3",
                        data=audio_bytes,
                        file_name=os.path.basename(audio_path),
                        mime="audio/mp3",
                        key=f"dl_{i}"
                    )
                except Exception:
                    pass

            # Add to Bookmarks (from saved project audio)
            st.markdown("### Add to Bookmarks")
            bm_c1, bm_c2 = st.columns([2, 1])
            with bm_c1:
                default_bm_name = f"{project.get('name') or 'Project'}"
                add_bm_name = st.text_input("Bookmark Name", value=default_bm_name, key=f"proj_bm_name_{i}")
            with bm_c2:
                btn_disabled = not (audio_path and os.path.exists(audio_path))
                if st.button("➕ Add to Bookmarks", key=f"proj_add_bm_btn_{i}", disabled=btn_disabled):
                    try:
                        with open(audio_path, 'rb') as f:
                            audio_bytes = f.read()
                        snippet = (project.get('rewritten_text') or project.get('original_text') or '')[:280]
                        save_bookmark_from_bytes(
                            name=add_bm_name,
                            source_project=project.get('name') or 'Project',
                            text_snippet=snippet,
                            tone=project.get('tone',''),
                            voice=project.get('voice',''),
                            audio_bytes=audio_bytes,
                        )
                        st.success("Bookmark saved from project audio.")
                    except Exception as e:
                        st.error(f"Failed to add bookmark: {e}")

            # Actions: Rename / Delete
            st.markdown("---")
            c1, c2, c3 = st.columns([2, 1, 1])
            with c1:
                new_name = st.text_input("Rename project to", value=project.get('name', ''), key=f"proj_rename_{i}")
            with c2:
                if st.button("✏️ Rename", key=f"proj_rename_btn_{i}"):
                    rename_project(project, new_name)
                    st.rerun()
            with c3:
                if st.button("🗑️ Delete", key=f"proj_delete_btn_{i}"):
                    delete_project(project)
                    st.rerun()


def main():
    """Main application function"""

    # Initialize services
    tts_service, llm_service = initialize_services()

    # Load bookmarks from disk once per session
    if 'bookmarks_loaded' not in st.session_state:
        load_bookmarks_from_disk()
    # Load library from disk once per session
    if 'library_loaded' not in st.session_state:
        load_library_from_disk()

    # Sidebar open/close state
    if 'nav_open' not in st.session_state:
        st.session_state.nav_open = True

    # Handle query params (?nav=open|close|toggle) from floating hamburger
    try:
        q = st.experimental_get_query_params()
        nav = (q.get('nav') or [None])[0]
        if nav == 'open':
            st.session_state.nav_open = True
            st.experimental_set_query_params()
        elif nav == 'close':
            st.session_state.nav_open = False
            st.experimental_set_query_params()
        elif nav == 'toggle':
            st.session_state.nav_open = not st.session_state.nav_open
            st.experimental_set_query_params()
    except Exception:
        pass

    # Inject CSS to hide or show the Streamlit sidebar
    if not st.session_state.nav_open:
        st.markdown(
            """
            <style>
            [data-testid='stSidebar']{
                transform: translateX(-110%);
                min-width: 0 !important;
                width: 0 !important;
                max-width: 0 !important;
                padding: 0 !important;
                margin: 0 !important;
            }
            </style>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            """
            <style>
            [data-testid='stSidebar']{ transform: translateX(0); }
            </style>
            """,
            unsafe_allow_html=True,
        )

    # Floating controls
    # Hamburger (only when sidebar is closed)
    if not st.session_state.nav_open:
        st.markdown("<a class='ev-hamburger' href='?nav=open'>☰</a>", unsafe_allow_html=True)

    # Sidebar
    with st.sidebar:
        # Header row: theme toggle icon, title, and single close button
        hdr_l, hdr_c, hdr_r = st.columns([0.15, 0.7, 0.15])
        with hdr_l:
            theme_icon = "☀️" if st.session_state.theme == 'Dark' else "🌙"
            if st.button(theme_icon, help="Toggle theme", key="sidebar_theme_toggle"):
                st.session_state.theme = 'Light' if st.session_state.theme == 'Dark' else 'Dark'
                apply_theme(st.session_state.theme == 'Dark')
                st.rerun()
        with hdr_c:
            st.markdown("# 🎧 EchoVerse")
    
        st.markdown("---")

        # Navigation (buttons instead of radio)
        if 'current_page' not in st.session_state:
            st.session_state.current_page = "Create New Audio"

        nav_items = [
            ("Create New Audio", "➕ Create New Audio", "nav_btn_create"),
            ("Library", "📚 Library", "nav_btn_library"),
            ("Audio Bookmarks", "🔖 Audio Bookmarks", "nav_btn_bookmarks"),
            ("Account", "⚙️ Account", "nav_btn_account"),
        ]

        for key_name, label, btn_key in nav_items:
            clicked = st.button(label, use_container_width=True, key=btn_key)
            if clicked:
                st.session_state.current_page = key_name

        page = st.session_state.current_page

        st.markdown("---")

        # Service Status
        st.markdown("### Service Status")

        # TTS Status
        tts_status = "✅ Connected" if tts_service.is_service_available() else "❌ Not Connected"
        st.markdown(f"**Text-to-Speech:** {tts_status}")

        # LLM Status
        llm_status = "✅ Connected" if llm_service.is_service_available() else "❌ Not Connected"
        st.markdown(f"**Text Rewriting:** {llm_status}")

        if not (tts_service.is_service_available() and llm_service.is_service_available()):
            st.warning("⚠️ Please check your API configuration in the .env file")

    # Main content area
    if page == "Create New Audio":
        create_audio_page(tts_service, llm_service)
    elif page == "Library":
        library_page()
    elif page == "Audio Bookmarks":
        bookmarks_page()
    elif page == "Account":
        account_page()


def create_audio_page(tts_service, llm_service):
    """Create new audio page"""
    st.markdown('<div class="main-header">Create New Audiobook</div>', unsafe_allow_html=True)

    # Project Information
    col1, col2 = st.columns(2)

    with col1:
        project_name = st.text_input("📝 Project Name", placeholder="Enter project name...")

    with col2:
        project_description = st.text_input("📄 Description", placeholder="Brief description...")

    # Text Input Section
    st.markdown('<div class="section-header">📖 Text Input</div>', unsafe_allow_html=True)

    input_method = st.radio("Choose input method:", ["Type/Paste Text", "Upload .txt File"])

    user_text = ""

    if input_method == "Type/Paste Text":
        user_text = st.text_area(
            "Enter your text:",
            height=200,
            placeholder="Paste or type your text here...",
            help=f"Maximum {Config.MAX_TEXT_LENGTH} words for optimal performance",
        )
    else:
        uploaded_file = st.file_uploader("Choose a .txt file", type=['txt'])
        if uploaded_file is not None:
            user_text = str(uploaded_file.read(), "utf-8")
            st.text_area("File content preview:", user_text, height=150, disabled=True)

    if not user_text.strip():
        st.info("Please enter some text to continue.")
        return

    # Word count check
    word_count = len(user_text.split())
    if word_count > Config.MAX_TEXT_LENGTH:
        st.warning(
            f"Text is {word_count} words. Consider reducing to under {Config.MAX_TEXT_LENGTH} words for better performance."
        )

    # Tone Selection
    st.markdown('<div class="section-header">🎭 Tone Selection</div>', unsafe_allow_html=True)

    col1, col2 = st.columns([2, 1])

    with col1:
        selected_tone = st.selectbox(
            "Choose the tone for your audiobook:",
            Config.TONE_OPTIONS,
            help="Select how you want your text to be rewritten",
        )

    with col2:
        if st.button("🔄 Suggest Rewrite", type="primary"):
            if llm_service.is_service_available():
                with st.spinner("Rewriting text with Granite..."):
                    rewritten_text = llm_service.rewrite_text(user_text, selected_tone)
                    st.session_state.rewritten_text = rewritten_text
                    st.success("Text rewritten successfully!")
            else:
                st.error("LLM service not available. Please check your configuration.")

    # Text Comparison
    if 'rewritten_text' in st.session_state:
        st.markdown('<div class="section-header">📋 Text Comparison</div>', unsafe_allow_html=True)

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("**Original Text**")
            st.text_area(
                "Original",
                user_text,
                height=300,
                key="original_display",
                disabled=True,
                label_visibility="collapsed",
            )

        with col2:
            st.markdown("**Rewritten Text**")
            rewritten_display = st.text_area(
                "Rewritten",
                st.session_state.rewritten_text,
                height=300,
                key="rewritten_display",
                label_visibility="collapsed",
            )
            st.session_state.rewritten_text = rewritten_display

    # Voice Selection and Audio Generation
    # Always show this section after text is provided. If no rewritten text is available,
    # fall back to the user's original text for TTS.
    st.markdown('<div class="section-header">🎤 Voice & Audio Generation</div>', unsafe_allow_html=True)

    col1, col2, col3 = st.columns([2, 1, 1])

    with col1:
        selected_voice = st.selectbox(
            "Choose voice:",
            tts_service.get_available_voices(),
            help="Select the voice for narration",
        )

    with col2:
        generate_audio = st.button("🎵 Generate Audio", type="primary")

    with col3:
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

    # Determine which text should be spoken: rewritten text if available, otherwise the original user text
    effective_text = st.session_state.get('rewritten_text', user_text)

    # Generate audio
    if generate_audio:
        if tts_service.is_service_available():
            with st.spinner("Generating audio..."):
                try:
                    audio_data = tts_service.synthesize_speech(
                        effective_text,
                        selected_voice,
                    )
                    st.session_state.audio_data = audio_data
                    st.success("Audio generated successfully!")
                except Exception as e:
                    st.error(f"Error generating audio: {str(e)}")
        else:
            st.error("TTS service not available. Please check your configuration.")

    # Audio playback and download
    if 'audio_data' in st.session_state:
        st.markdown('<div class="section-header">🔊 Audio Playback</div>', unsafe_allow_html=True)

        # Audio player
        st.audio(st.session_state.audio_data, format='audio/mp3')

        # Download button
        st.download_button(
            label="⬇️ Download MP3",
            data=st.session_state.audio_data,
            file_name=f"{project_name or 'audiobook'}.mp3",
            mime="audio/mp3",
        )

        # Add as Bookmark UI
        st.markdown("<div class='section-header'>🔖 Add Bookmark</div>", unsafe_allow_html=True)
        bm_cols = st.columns([2, 1])
        with bm_cols[0]:
            default_bm_name = f"{project_name or 'Untitled'}"
            bookmark_name = st.text_input("Bookmark Name", value=default_bm_name, key="bm_name")
        with bm_cols[1]:
            if st.button("➕ Save as Bookmark", key="save_bookmark_btn"):
                save_bookmark(
                    name=bookmark_name,
                    source_project=project_name or 'Untitled',
                    text_snippet=(st.session_state.get('rewritten_text') or user_text or '')[:280],
                    tone=selected_tone,
                    voice=selected_voice,
                )
    else:
        # No audio yet: offer to create an empty bookmark now
        st.markdown("<div class='section-header'>🔖 Create Bookmark (no audio yet)</div>", unsafe_allow_html=True)
        bm2_cols = st.columns([2, 1])
        with bm2_cols[0]:
            default_bm_name2 = f"{project_name or 'Untitled'}"
            bookmark_name2 = st.text_input("Bookmark Name", value=default_bm_name2, key="bm_name_no_audio")
        with bm2_cols[1]:
            if st.button("➕ Create Empty Bookmark", key="create_empty_bm_btn"):
                create_empty_bookmark(
                    name=bookmark_name2,
                    source_project=project_name or 'Untitled',
                    text_snippet=(st.session_state.get('rewritten_text') or user_text or '')[:280],
                    tone=selected_tone,
                    voice=selected_voice,
                )


def library_page():
    """Library page to view saved projects"""
    st.markdown('<div class="main-header">📚 Your Library</div>', unsafe_allow_html=True)
    display_library()


def bookmarks_page():
    """Bookmarks page"""
    st.markdown('<div class="main-header">🔖 Audio Bookmarks</div>', unsafe_allow_html=True)
    # Load from disk if not loaded
    if 'bookmarks_loaded' not in st.session_state:
        load_bookmarks_from_disk()
    display_bookmarks()


def account_page():
    """Account settings page"""
    st.markdown('<div class="main-header">👤 Account Settings</div>', unsafe_allow_html=True)

    st.markdown("### API Configuration")
    st.info("Configure your IBM Watson API keys in the .env file")

    st.markdown("### Usage Statistics")
    if 'library' in st.session_state:
        st.metric("Projects Created", len(st.session_state.library))
    else:
        st.metric("Projects Created", 0)


if __name__ == "__main__":
    _configure_page()
    _init_theme()
    main()
