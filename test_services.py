#!/usr/bin/env python3
"""
EchoVerse Service Test Script
This script tests the IBM Watson services integration
"""

import sys
import os
from services.watson_tts import WatsonTTSService
from services.watsonx_llm import WatsonxLLMService

def test_tts_service():
    """Test Watson Text-to-Speech service"""
    print("🎤 Testing Watson Text-to-Speech service...")
    
    try:
        tts_service = WatsonTTSService()
        
        if not tts_service.is_service_available():
            print("❌ TTS service not available - check your API configuration")
            return False
        
        # Test voice list
        voices = tts_service.get_available_voices()
        print(f"✅ Available voices: {', '.join(voices)}")
        
        # Test synthesis with short text
        test_text = "Hello, this is a test of the EchoVerse text-to-speech system."
        print("🔊 Testing audio synthesis...")
        
        audio_data = tts_service.synthesize_speech(test_text, 'Lisa')
        
        if audio_data and len(audio_data) > 0:
            print(f"✅ Audio generated successfully ({len(audio_data)} bytes)")
            return True
        else:
            print("❌ No audio data generated")
            return False
            
    except Exception as e:
        print(f"❌ TTS test failed: {str(e)}")
        return False

def test_llm_service():
    """Test Watsonx LLM service"""
    print("\n🤖 Testing Watsonx LLM service...")
    
    try:
        llm_service = WatsonxLLMService()
        
        if not llm_service.is_service_available():
            print("❌ LLM service not available - check your API configuration")
            return False
        
        # Test text rewriting
        test_text = "The weather is nice today. It's sunny and warm outside."
        print("📝 Testing text rewriting...")
        
        rewritten_text = llm_service.rewrite_text(test_text, 'Inspiring')
        
        if rewritten_text and rewritten_text != test_text:
            print(f"✅ Text rewritten successfully")
            print(f"Original: {test_text}")
            print(f"Rewritten: {rewritten_text}")
            return True
        else:
            print("❌ Text rewriting failed or returned unchanged text")
            return False
            
    except Exception as e:
        print(f"❌ LLM test failed: {str(e)}")
        return False

def check_configuration():
    """Check if configuration is properly set up"""
    print("🔧 Checking configuration...")
    
    from config import Config
    
    # Check TTS configuration
    if not Config.WATSON_TTS_API_KEY:
        print("❌ Watson TTS API key not configured")
        return False
    else:
        print("✅ Watson TTS API key configured")
    
    # Check LLM configuration
    if not Config.WATSONX_API_KEY:
        print("❌ Watsonx API key not configured")
        return False
    else:
        print("✅ Watsonx API key configured")
    
    if not Config.WATSONX_PROJECT_ID:
        print("❌ Watsonx Project ID not configured")
        return False
    else:
        print("✅ Watsonx Project ID configured")
    
    return True

def main():
    """Main test function"""
    print("🧪 EchoVerse Service Tests")
    print("=" * 50)
    
    # Check if .env file exists
    if not os.path.exists('.env'):
        print("❌ .env file not found")
        print("Please copy .env.example to .env and configure your API keys")
        sys.exit(1)
    
    # Check configuration
    if not check_configuration():
        print("\n❌ Configuration incomplete")
        print("Please check your .env file and ensure all required API keys are set")
        sys.exit(1)
    
    # Test services
    tts_success = test_tts_service()
    llm_success = test_llm_service()
    
    print("\n" + "=" * 50)
    
    if tts_success and llm_success:
        print("🎉 All tests passed! EchoVerse is ready to use.")
        print("Run 'streamlit run app.py' to start the application")
    else:
        print("❌ Some tests failed. Please check your configuration and try again.")
        if not tts_success:
            print("   - Watson Text-to-Speech service needs attention")
        if not llm_success:
            print("   - Watsonx LLM service needs attention")

if __name__ == "__main__":
    main()
