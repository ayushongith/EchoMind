from flask import Flask, render_template, request, jsonify
from google.generativeai import configure, GenerativeModel
import os
from gtts import gTTS
import base64
from io import BytesIO

app = Flask(__name__)

# Configure Google Gemini API
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
configure(api_key=GOOGLE_API_KEY)
model = GenerativeModel('gemini-pro')

chat_history = []

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/process_input', methods=['POST'])
async def process_input():
    user_input = request.json.get('input', '')
    
    # Add user message to chat history
    chat_history.append({'role': 'user', 'parts': [user_input]})
    
    try:
        # Generate response using Gemini
        response = await model.generate_content_async(chat_history)
        ai_response = response.text
        
        # Add AI response to chat history
        chat_history.append({'role': 'model', 'parts': [ai_response]})
        
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
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
