from flask import Flask, render_template, request, jsonify
import os
from gtts import gTTS
import base64
from io import BytesIO
import requests
from dotenv import load_dotenv

app = Flask(__name__)

# Load environment variables
load_dotenv()

# Configure OpenRouter API
OPENROUTER_API_KEY = os.getenv('OPENROUTER_API_KEY')
MODEL = "deepseek-ai/deepseek-r1-0528-qwen3-8b"  # Free model on OpenRouter

if not OPENROUTER_API_KEY:
    raise ValueError("OPENROUTER_API_KEY not found in environment variables")

chat_history = []

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/process_input', methods=['POST'])
def process_input():
    user_input = request.json.get('input', '')
    
    # Add user message to chat history
    chat_history.append({"role": "user", "content": user_input})
    
    try:
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
        
        if response.status_code == 200:
            data = response.json()
            if 'choices' in data and len(data['choices']) > 0:
                ai_response = data['choices'][0]['message']['content']
                
                # Add AI response to chat history
                chat_history.append({"role": "assistant", "content": ai_response})
                
                # Convert response to speech
                tts = gTTS(text=ai_response, lang='en')
                audio_buffer = BytesIO()
                tts.write_to_fp(audio_buffer)
                audio_buffer.seek(0)
                audio_base64 = base64.b64encode(audio_buffer.read()).decode('utf-8')
                
                return jsonify({
                    'text': ai_response,
                    'audio': audio_base64
                })
            else:
                raise Exception("Unexpected response format from OpenRouter")
        else:
            error_msg = f"OpenRouter API error: {response.status_code} - {response.text}"
            print(error_msg)
            return jsonify({'error': error_msg}), 500
            
    except Exception as e:
        import traceback
        error_msg = f"Error: {str(e)}\n{traceback.format_exc()}"
        print(error_msg)
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
