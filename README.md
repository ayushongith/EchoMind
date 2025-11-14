# EchoMind - Web Voice Assistant

EchoMind is a full-stack web-based voice assistant powered by OpenRouter API. It supports both text and voice input, with text-to-speech responses.

## Features

- 🎙️ Voice input using Web Speech API
- ✍️ Text input option
- 🔊 Text-to-speech responses
- 💬 Chat-style conversation history
- 🎨 Responsive and modern UI
- 🔄 Real-time interaction

## Prerequisites

- Python 3.8+
- OpenRouter API key (get one at [openrouter.ai](https://openrouter.ai))
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
   Create a `.env` file in the project root and add your OpenRouter API key:
   ```
   OPENROUTER_API_KEY=your_api_key_here
   ```

## Running the Application

### Web Mode (Recommended)

1. **Start the Flask server**
   ```bash
   python app.py
   ```

2. **Open your browser**
   Go to `http://localhost:5000` to access EchoMind.

### CLI Mode (Alternative)

For command-line voice interaction:
```bash
python voice_assistant.py
```

This mode uses direct microphone input and local audio processing.

## Configuration

### AI Model

The default AI model is `deepseek-ai/deepseek-r1-0528-qwen3-8b` (a free model on OpenRouter). You can change this by modifying the `MODEL` variable in `app.py` or `voice_assistant.py`.

Available models on OpenRouter include:
- `openai/gpt-3.5-turbo` - Fast and cost-effective
- `openai/gpt-4` - More capable but higher cost
- `deepseek-ai/deepseek-r1-0528-qwen3-8b` - Free tier option
- Many others available at [openrouter.ai/models](https://openrouter.ai/models)

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
   - `OPENROUTER_API_KEY`: Your OpenRouter API key
4. Set the build command: `pip install -r requirements.txt`
5. Set the start command: `python app.py`
6. Deploy!

## Troubleshooting

- **Microphone Access**: Ensure you've allowed microphone access in your browser
- **API Key**: Verify your OpenRouter API key is set correctly in the `.env` file
- **Browser Support**: For best results, use the latest version of Chrome or Edge
- **API Errors**: Check the `/test_api` endpoint to verify your API key is working

## License

This project is open source and available under the [MIT License](LICENSE).

## Acknowledgements

- [OpenRouter API](https://openrouter.ai/) - AI model access
- [Flask](https://flask.palletsprojects.com/) - Web framework
- [Tailwind CSS](https://tailwindcss.com/) - Styling
- [gTTS](https://gtts.readthedocs.io/) - Text-to-speech
- [SpeechRecognition](https://github.com/Uberi/speech_recognition) - Speech-to-text
