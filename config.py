import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Configuration class for EchoVerse application"""
    
    # IBM Watson Text-to-Speech Configuration
    WATSON_TTS_API_KEY = (os.getenv('IBM_WATSON_API_KEY') or '').strip()
    WATSON_TTS_URL = (os.getenv('IBM_WATSON_URL', 'https://api.us-south.text-to-speech.watson.cloud.ibm.com') or '').strip()
    
    # IBM Watsonx Configuration
    WATSONX_API_KEY = (os.getenv('IBM_WATSONX_API_KEY') or '').strip()
    WATSONX_PROJECT_ID = (os.getenv('IBM_WATSONX_PROJECT_ID') or '').strip()
    WATSONX_URL = (os.getenv('IBM_WATSONX_URL', 'https://us-south.ml.cloud.ibm.com') or '').strip()

    # Hugging Face
    HUGGINGFACE_TOKEN = (os.getenv('HUGGINGFACE_TOKEN') or '').strip()
    HF_SPACE_ID = (os.getenv('HF_SPACE_ID') or 'sabarnakb/GraniteEchoverse').strip()
    HF_SPACE_API_NAME = (os.getenv('HF_SPACE_API_NAME') or '/process_text').strip()
    HF_FALLBACK_MODEL_ID = (os.getenv('HF_FALLBACK_MODEL_ID') or 'google/flan-t5-base').strip()

    # Application Configuration
    MAX_TEXT_LENGTH = 2000  # Maximum words for performance requirement
    SUPPORTED_VOICES = {
        'Lisa': 'en-US_LisaV3Voice',
        'Michael': 'en-US_MichaelV3Voice',
        'Allison': 'en-US_AllisonV3Voice'
    }
    
    TONE_OPTIONS = ['Neutral', 'Suspenseful', 'Inspiring']
    
    # Audio Configuration
    AUDIO_FORMAT = 'audio/mp3'
    SAMPLE_RATE = 22050

    # Network/Retry Configuration
    REQUEST_TIMEOUT = float(os.getenv('ECHOVERSE_REQUEST_TIMEOUT', '15'))  # seconds
    REQUEST_RETRIES = int(os.getenv('ECHOVERSE_REQUEST_RETRIES', '3'))
    RETRY_BACKOFF = float(os.getenv('ECHOVERSE_RETRY_BACKOFF', '0.75'))  # seconds

    # Local Library Configuration
    # Default directory where projects (text + audio) are stored locally
    LIBRARY_DIR = os.getenv('ECHOVERSE_LIBRARY_DIR') or os.path.join(os.path.dirname(__file__), 'library')
    # Default directory where audio bookmarks are stored locally
    BOOKMARKS_DIR = os.getenv('ECHOVERSE_BOOKMARKS_DIR') or os.path.join(os.path.dirname(__file__), 'bookmarks')
