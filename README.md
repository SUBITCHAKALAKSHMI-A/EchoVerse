# 🎧 EchoVerse - AI Audiobook Creator

EchoVerse is a generative AI-based audiobook creation system that converts user-provided text into expressive audio with selectable tones and voices. The application enhances accessibility for students, professionals, and visually impaired users by enabling them to transform text into natural-sounding narration with customization options.

## ✨ Features

- **📝 Text Input**: Accept manual text input or .txt file uploads
- **🎭 Tone Rewriting**: Transform text into Neutral, Suspenseful, or Inspiring tones using IBM Watsonx Granite LLM
- **🎤 Voice Selection**: Choose from multiple high-quality voices (Lisa, Michael, Allison)
- **📋 Side-by-Side Comparison**: View original and rewritten text side by side
- **🔊 Audio Generation**: Create expressive audio narration using IBM Watson Text-to-Speech
- **⬇️ Download & Stream**: Play audio directly in the browser or download as MP3
- **📚 Library Management**: Save and organize your audiobook projects
- **🎨 Modern UI**: Clean, accessible Streamlit-based interface

## 🚀 Quick Start

### Prerequisites

- Python 3.10 or higher
- IBM Cloud account with Watson services
- IBM Watsonx access

### Installation

1. **Clone or download the project**
   ```bash
   cd EchoVerse
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure API Keys**
   - Copy `.env.example` to `.env`
   - Add your IBM Watson API credentials:
   
   ```env
   # IBM Watson Text-to-Speech
   IBM_WATSON_API_KEY=your_watson_tts_api_key
   IBM_WATSON_URL=https://api.us-south.text-to-speech.watson.cloud.ibm.com
   
   # IBM Watsonx
   IBM_WATSONX_API_KEY=your_watsonx_api_key
   IBM_WATSONX_PROJECT_ID=your_watsonx_project_id
   IBM_WATSONX_URL=https://us-south.ml.cloud.ibm.com
   ```

4. **Run the application**
   ```bash
   streamlit run app.py
   ```

5. **Open your browser** to `http://localhost:8501`

## 🔧 Configuration

### Getting IBM Watson API Keys

1. **IBM Watson Text-to-Speech**:
   - Go to [IBM Cloud Console](https://cloud.ibm.com/)
   - Create a Text to Speech service instance
   - Copy the API key and service URL

2. **IBM Watsonx**:
   - Access [IBM Watsonx](https://www.ibm.com/watsonx)
   - Create a project and note the project ID
   - Generate API key from IBM Cloud IAM

### Supported Voices

- **Lisa**: Clear, professional female voice
- **Michael**: Warm, engaging male voice  
- **Allison**: Expressive, friendly female voice

### Tone Options

- **Neutral**: Clear, professional, and straightforward
- **Suspenseful**: Dramatic, engaging, builds tension
- **Inspiring**: Motivational, uplifting, empowering

## 📖 Usage Guide

### Creating Your First Audiobook

1. **Navigate to "Create New Audio"**
2. **Enter project details**: Name and description
3. **Input your text**: Type directly or upload a .txt file
4. **Select tone**: Choose Neutral, Suspenseful, or Inspiring
5. **Generate rewrite**: Click "Suggest Rewrite" to transform your text
6. **Review comparison**: Check original vs rewritten text side by side
7. **Choose voice**: Select from Lisa, Michael, or Allison
8. **Generate audio**: Click "Generate Audio" to create your audiobook
9. **Play & download**: Listen in-browser or download MP3 file
10. **Save to library**: Store your project for future access

### Managing Your Library

- View all saved projects in the Library section
- Each project stores original text, rewritten version, tone, and voice settings
- Easily recreate or modify existing audiobooks

## 🏗️ Architecture

```
EchoVerse/
├── app.py                 # Main Streamlit application
├── config.py              # Configuration management
├── requirements.txt       # Python dependencies
├── .env.example          # Environment variables template
├── services/
│   ├── __init__.py
│   ├── watson_tts.py     # IBM Watson Text-to-Speech integration
│   └── watsonx_llm.py    # IBM Watsonx LLM integration
└── README.md             # This file
```

## 🔒 Security & Privacy

- **No persistent data storage**: User data is only stored in session state
- **API key protection**: Store credentials in environment variables
- **Local processing**: All text processing happens through secure IBM APIs
- **No data retention**: IBM Watson services don't retain user data by default

## ⚡ Performance

- **Optimized for texts under 2000 words** for best performance
- **Audio generation typically completes in under 10 seconds**
- **Streaming playback** for immediate audio preview
- **Efficient caching** of service connections

## 🛠️ Troubleshooting

### Common Issues

1. **"Service not available" errors**
   - Check your API keys in the `.env` file
   - Verify IBM Cloud service instances are active
   - Ensure proper internet connectivity

2. **Audio generation fails**
   - Verify Watson Text-to-Speech service is provisioned
   - Check text length (reduce if over 2000 words)
   - Ensure selected voice is available in your region

3. **Text rewriting doesn't work**
   - Confirm Watsonx project ID is correct
   - Check Watsonx API key permissions
   - Verify project has access to Granite models

### Getting Help

- Check the service status indicators in the sidebar
- Review error messages in the Streamlit interface
- Verify API credentials and service provisioning

## 🚀 Deployment

### Local Development
```bash
streamlit run app.py
```

### Streamlit Cloud
1. Push code to GitHub repository
2. Connect to Streamlit Cloud
3. Add environment variables in Streamlit Cloud settings
4. Deploy automatically

### Docker (Optional)
```dockerfile
FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8501
CMD ["streamlit", "run", "app.py"]
```

## 📋 Requirements

### Functional Requirements
- ✅ Accept user input text or .txt file
- ✅ Rewrite text using IBM Watsonx Granite LLM
- ✅ Generate audio using IBM Watson Text-to-Speech
- ✅ Provide side-by-side text comparison
- ✅ Support multiple voices and tones
- ✅ Enable audio playback and MP3 download
- ✅ Streamlit-based user interface

### Non-Functional Requirements
- ✅ **Usability**: Intuitive, accessible interface
- ✅ **Performance**: <10 second audio generation for <2000 words
- ✅ **Reliability**: Comprehensive error handling
- ✅ **Portability**: Runs locally and in cloud environments
- ✅ **Security**: No persistent user data storage

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- **IBM Watson** for Text-to-Speech and Watsonx services
- **Streamlit** for the amazing web framework
- **The EchoVerse Team** for making audiobooks accessible to everyone

---

**Made with ❤️ for accessibility and learning**
