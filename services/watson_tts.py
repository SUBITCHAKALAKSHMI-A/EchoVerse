import io
import base64
from ibm_watson import TextToSpeechV1
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from config import Config
import streamlit as st

class WatsonTTSService:
    """IBM Watson Text-to-Speech service integration"""
    
    def __init__(self):
        self.authenticator = None
        self.text_to_speech = None
        self._initialize_service()
    
    def _initialize_service(self):
        """Initialize Watson TTS service"""
        try:
            if not Config.WATSON_TTS_API_KEY:
                raise ValueError("Watson TTS API key not found in configuration")
            
            self.authenticator = IAMAuthenticator(Config.WATSON_TTS_API_KEY)
            self.text_to_speech = TextToSpeechV1(authenticator=self.authenticator)
            self.text_to_speech.set_service_url(Config.WATSON_TTS_URL)
            
        except Exception as e:
            st.error(f"Failed to initialize Watson TTS service: {str(e)}")
            self.text_to_speech = None
    
    def synthesize_speech(self, text: str, voice: str = 'Lisa') -> bytes:
        """
        Convert text to speech using Watson TTS
        
        Args:
            text (str): Text to convert to speech
            voice (str): Voice to use for synthesis
            
        Returns:
            bytes: Audio data in MP3 format
        """
        if not self.text_to_speech:
            raise Exception("Watson TTS service not initialized")
        
        try:
            # Get voice ID from configuration
            voice_id = Config.SUPPORTED_VOICES.get(voice, Config.SUPPORTED_VOICES['Lisa'])
            
            # Synthesize speech
            response = self.text_to_speech.synthesize(
                text=text,
                voice=voice_id,
                accept='audio/mp3'
            ).get_result()
            
            # Return audio content
            return response.content
            
        except Exception as e:
            st.error(f"Error synthesizing speech: {str(e)}")
            raise
    
    def get_available_voices(self) -> list:
        """Get list of available voices"""
        return list(Config.SUPPORTED_VOICES.keys())
    
    def is_service_available(self) -> bool:
        """Check if the service is properly initialized"""
        return self.text_to_speech is not None
