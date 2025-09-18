#!/usr/bin/env python3
"""
EchoVerse Setup Script
This script helps users set up the EchoVerse application
"""

import os
import sys
import subprocess
import shutil

def check_python_version():
    """Check if Python version is 3.10 or higher"""
    if sys.version_info < (3, 10):
        print("❌ Python 3.10 or higher is required")
        print(f"Current version: {sys.version}")
        return False
    print(f"✅ Python version: {sys.version}")
    return True

def install_requirements():
    """Install required packages"""
    print("\n📦 Installing required packages...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ All packages installed successfully")
        return True
    except subprocess.CalledProcessError:
        print("❌ Failed to install packages")
        return False

def setup_env_file():
    """Set up environment file"""
    print("\n🔧 Setting up environment configuration...")
    
    if os.path.exists('.env'):
        print("⚠️  .env file already exists")
        response = input("Do you want to overwrite it? (y/N): ")
        if response.lower() != 'y':
            print("Skipping .env setup")
            return True
    
    if os.path.exists('.env.example'):
        shutil.copy('.env.example', '.env')
        print("✅ Created .env file from template")
        print("\n🔑 Please edit the .env file and add your IBM Watson API credentials:")
        print("   - IBM_WATSON_API_KEY")
        print("   - IBM_WATSONX_API_KEY") 
        print("   - IBM_WATSONX_PROJECT_ID")
        return True
    else:
        print("❌ .env.example file not found")
        return False

def check_streamlit():
    """Check if Streamlit is properly installed"""
    print("\n🔍 Checking Streamlit installation...")
    try:
        import streamlit
        print(f"✅ Streamlit version: {streamlit.__version__}")
        return True
    except ImportError:
        print("❌ Streamlit not found")
        return False

def main():
    """Main setup function"""
    print("🎧 EchoVerse Setup")
    print("=" * 50)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Install requirements
    if not install_requirements():
        sys.exit(1)
    
    # Check Streamlit
    if not check_streamlit():
        sys.exit(1)
    
    # Setup environment file
    if not setup_env_file():
        sys.exit(1)
    
    print("\n🎉 Setup completed successfully!")
    print("\n📋 Next steps:")
    print("1. Edit the .env file with your IBM Watson API credentials")
    print("2. Run the application: streamlit run app.py")
    print("3. Open your browser to http://localhost:8501")
    print("\n📚 For detailed instructions, see README.md")

if __name__ == "__main__":
    main()
