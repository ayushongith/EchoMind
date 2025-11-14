from flask import Flask, render_template, request, jsonify
import os
from gtts import gTTS
import base64
from io import BytesIO
import requests
from dotenv import load_dotenv
from stt_engine import STTEngine
import tempfile
import speech_recognition as sr

app = Flask(__name__)

# Load environment variables
load_dotenv()

# Configure OpenRouter API
OPENROUTER_API_KEY = os.getenv('OPENROUTER_API_KEY')
MODEL = "openai/gpt-3.5-turbo"  # Standard model on OpenRouter

if not OPENROUTER_API_KEY:
    raise ValueError("OPENROUTER_API_KEY not found in environment variables")

# Debug: Print environment variables
print("\n=== Environment Variables ===")
print(f"OPENROUTER_API_KEY: {'*' * 8}{OPENROUTER_API_KEY[-4:] if OPENROUTER_API_KEY else 'None'}")
print("===========================\n")

chat_history = []

# Initialize STT engine for backend voice recognition
stt_engine = STTEngine(model_name="whisper")

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/process_input', methods=['POST'])
def process_input():
    try:
        if not request.is_json:
            raise ValueError("Request must be JSON")
            
        user_input = request.json.get('input', '')
        if not user_input:
            raise ValueError("Input cannot be empty")
        
        print(f"Received input: {user_input}")
        
        # Add user message to chat history
        chat_history.append({"role": "user", "content": user_input})
        
        if not OPENROUTER_API_KEY:
            raise ValueError("OpenRouter API key is not configured")
            
        headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://echomind-ai-assistant.com",
            "X-Title": "EchoMind Voice Assistant"
        }
        
        payload = {
            "model": MODEL,
            "messages": chat_history
        }
        
        # Make request to OpenRouter
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=30
        )
        
        print(f"OpenRouter response status: {response.status_code}")
        print(f"Response content: {response.text[:500]}")  # Log first 500 chars of response
        
        if response.status_code == 200:
            data = response.json()
            print(f"Parsed response data: {data}")
            
            if not isinstance(data, dict):
                raise ValueError(f"Unexpected response format: {type(data)}")
                
            if 'choices' not in data or not data['choices']:
                raise ValueError(f"No choices in response: {data}")
                
            if not isinstance(data['choices'], list) or len(data['choices']) == 0:
                raise ValueError(f"Invalid choices format: {data['choices']}")
                
            ai_response = data['choices'][0].get('message', {}).get('content')
            if not ai_response:
                raise ValueError(f"No content in response: {data}")
            
            print(f"Generated AI response: {ai_response[:100]}...")  # Log first 100 chars
            
            # Add AI response to chat history
            chat_history.append({"role": "assistant", "content": ai_response})
            
            # Convert response to speech
            try:
                tts = gTTS(text=ai_response, lang='en')
                audio_buffer = BytesIO()
                tts.write_to_fp(audio_buffer)
                audio_buffer.seek(0)
                audio_base64 = base64.b64encode(audio_buffer.read()).decode('utf-8')
                
                return jsonify({
                    'text': ai_response,
                    'audio': audio_base64
                })
            except Exception as tts_error:
                print(f"TTS Error: {str(tts_error)}")
                return jsonify({
                    'text': ai_response,
                    'audio': None,
                    'error': f"Text-to-speech error: {str(tts_error)}"
                })
        else:
            error_msg = f"OpenRouter API error: {response.status_code} - {response.text}"
            print(error_msg)
            return jsonify({'error': error_msg}), 500
            
    except Exception as e:
        import traceback
        error_msg = f"Error: {str(e)}\n{traceback.format_exc()}"
        print(error_msg)
        return jsonify({'error': str(e)}), 500

@app.route('/transcribe_audio', methods=['POST'])
def transcribe_audio():
    """Transcribe audio using backend Whisper STT engine."""
    try:
        if 'audio' not in request.files:
            return jsonify({'error': 'No audio file provided'}), 400
        
        audio_file = request.files['audio']
        if audio_file.filename == '':
            return jsonify({'error': 'No audio file selected'}), 400
        
        # Save uploaded audio to temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.webm') as temp_audio:
            audio_file.save(temp_audio.name)
            temp_audio_path = temp_audio.name
        
        try:
            # Use speech_recognition to process the audio
            recognizer = sr.Recognizer()
            
            # Convert audio file to format recognized by speech_recognition
            from pydub import AudioSegment
            
            # Load audio file (handles webm, mp3, wav, etc.)
            audio_segment = AudioSegment.from_file(temp_audio_path)
            
            # Convert to WAV format (16kHz, mono) for Whisper
            wav_io = BytesIO()
            audio_segment.export(wav_io, format="wav")
            wav_io.seek(0)
            
            # Use Whisper for transcription
            with sr.AudioFile(wav_io) as source:
                audio_data = recognizer.record(source)
                text = recognizer.recognize_whisper(
                    audio_data,
                    model="base",
                    language="english"
                )
            
            print(f"Transcribed text: {text}")
            return jsonify({'text': text.strip()})
            
        except sr.UnknownValueError:
            return jsonify({'error': 'Could not understand audio. Please speak more clearly.'}), 400
        except sr.RequestError as e:
            return jsonify({'error': f'Speech recognition service error: {str(e)}'}), 500
        except Exception as e:
            print(f"Transcription error: {str(e)}")
            import traceback
            traceback.print_exc()
            return jsonify({'error': f'Transcription failed: {str(e)}'}), 500
        finally:
            # Clean up temporary file
            if os.path.exists(temp_audio_path):
                os.unlink(temp_audio_path)
                
    except Exception as e:
        import traceback
        error_msg = f"Error processing audio: {str(e)}\n{traceback.format_exc()}"
        print(error_msg)
        return jsonify({'error': str(e)}), 500

@app.route('/test_api', methods=['GET'])
def test_api():
    try:
        print("\n=== Testing OpenRouter API ===")
        print(f"Using API key: {OPENROUTER_API_KEY[:5]}...{OPENROUTER_API_KEY[-5:]}")
        
        headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json"
        }
        
        # Test with a simple prompt
        payload = {
            "model": MODEL,
            "messages": [{"role": "user", "content": "Say 'test successful'"}]
        }
        
        print("Sending request to OpenRouter...")
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=10
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            return jsonify({
                "status": "success",
                "response": response.json()
            })
        else:
            return jsonify({
                "status": "error",
                "status_code": response.status_code,
                "response": response.text
            }), 500
            
    except Exception as e:
        import traceback
        error_msg = f"Error: {str(e)}\n{traceback.format_exc()}"
        print(error_msg)
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    print("\n=== Starting EchoMind Server ===")
    print(f"Debug mode: {app.debug}")
    print(f"OpenRouter API Key: {'Set' if OPENROUTER_API_KEY else 'Not set'}")
    print(f"Model: {MODEL}")
    print("Server running on http://127.0.0.1:5000")
    print("Test API endpoint: http://127.0.0.1:5000/test_api")
    print("==============================\n")
    app.run(debug=True, port=5000)
