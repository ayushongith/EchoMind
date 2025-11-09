# EchoMind - Web Voice Assistant

EchoMind is a full-stack web-based voice assistant powered by Google's Gemini API. It supports both text and voice input, with text-to-speech responses.

## Features

- 🎙️ Voice input using Web Speech API
- ✍️ Text input option
- 🔊 Text-to-speech responses
- 💬 Chat-style conversation history
- 🎨 Responsive and modern UI
- 🔄 Real-time interaction

## Prerequisites

- Python 3.8+
- Google Gemini API key
- Modern web browser with Web Speech API support (Chrome, Edge, Firefox, Safari)

## Setup Instructions

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/echomind.git
   cd echomind
   ```

2. **Create a virtual environment** (recommended)
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: .\venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   Create a `.env` file in the project root and add your Google Gemini API key:
   ```
   GOOGLE_API_KEY=your_api_key_here
   ```

## Running the Application

1. **Start the Flask server**
   ```bash
   python app.py
   ```

2. **Open your browser**
   Go to `http://localhost:5000` to access EchoMind.

## Usage

1. **Text Input**
   - Type your message in the input box
   - Press Enter or click the Send button

2. **Voice Input**
   - Click the microphone button
   - Allow microphone access when prompted
   - Speak your message clearly
   - Click the stop button or wait for the recording to end

3. **Audio Playback**
   - The assistant's response will be played automatically
   - Use the audio player controls to replay or adjust volume

## Deployment

### Render (Recommended for Free Tier)

1. Create a new Web Service on Render
2. Connect your GitHub repository
3. Set the following environment variables:
   - `PYTHON_VERSION`: 3.9
   - `GOOGLE_API_KEY`: Your Gemini API key
4. Set the build command: `pip install -r requirements.txt`
5. Set the start command: `python app.py`
6. Deploy!

## Troubleshooting

- **Microphone Access**: Ensure you've allowed microphone access in your browser
- **API Key**: Verify your Google Gemini API key is set correctly
- **Browser Support**: For best results, use the latest version of Chrome or Edge

## License

This project is open source and available under the [MIT License](LICENSE).

## Acknowledgements

- [Google Gemini API](https://ai.google.dev/)
- [Flask](https://flask.palletsprojects.com/)
- [Tailwind CSS](https://tailwindcss.com/)
- [gTTS](https://gtts.readthedocs.io/)
