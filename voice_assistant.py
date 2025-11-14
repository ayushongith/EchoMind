import os
import logging
import json
import asyncio
from typing import List, Dict, Optional
from dotenv import load_dotenv

# Import our modules
from audio_capture import AudioCapture
from stt_engine import STTEngine
from ai_processor import AIProcessor
from tts_engine import TTSEngine

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('assistant.log')
    ]
)
logger = logging.getLogger(__name__)

class VoiceAssistant:
    def __init__(self):
        """Initialize the voice assistant with all required components."""
        # Load environment variables
        load_dotenv()
        
        # Initialize components
        self.audio_capture = AudioCapture(sample_rate=16000, chunk_size=1024)
        self.stt_engine = STTEngine(model_name="whisper")
        self.ai_processor = AIProcessor(
            api_key=os.getenv("OPENROUTER_API_KEY"),
            model="openai/gpt-3.5-turbo"
        )
        self.tts_engine = TTSEngine(engine="edge", voice="en-US-AriaNeural")
        
        # Conversation history
        self.conversation_history: List[Dict[str, str]] = []
        
        # System prompt
        self.system_prompt = """
        You are EchoMind, a helpful and friendly AI assistant. 
        Keep your responses concise and natural-sounding for voice interaction.
        """
    
    async def process_voice_input(self) -> Optional[str]:
        """Process voice input from the user."""
        try:
            # Start audio capture
            with self.audio_capture as ac:
                print("Listening... (press Ctrl+C to stop)")
                audio_data = ac.record_until_silence()
            
            if audio_data.size == 0:
                logger.warning("No audio data captured")
                return None
                
            # Convert speech to text
            text = self.stt_engine.audio_to_text(audio_data)
            if not text:
                logger.warning("Could not transcribe audio")
                return None
                
            logger.info(f"You said: {text}")
            return text
            
        except Exception as e:
            logger.error(f"Error processing voice input: {str(e)}")
            return None
    
    async def generate_response(self, user_input: str) -> Optional[bytes]:
        """Generate a voice response to the user's input."""
        try:
            # Get AI response
            ai_response = self.ai_processor.process_conversation(
                user_input=user_input,
                conversation_history=self.conversation_history,
                system_prompt=self.system_prompt
            )
            
            if not ai_response:
                logger.error("Failed to get AI response")
                return None
            
            logger.info(f"AI: {ai_response}")
            
            # Update conversation history
            self.conversation_history.append({"role": "user", "content": user_input})
            self.conversation_history.append({"role": "assistant", "content": ai_response})
            
            # Limit conversation history to last 10 exchanges (20 messages)
            if len(self.conversation_history) > 20:
                self.conversation_history = self.conversation_history[-20:]
            
            # Convert text to speech
            audio_data = await self.tts_engine.text_to_speech_async(ai_response)
            return audio_data
            
        except Exception as e:
            logger.error(f"Error generating response: {str(e)}")
            return None
    
    async def run_conversation_loop(self):
        """Run the main conversation loop."""
        print("\n" + "="*50)
        print("EchoMind Voice Assistant")
        print("Press Ctrl+C to exit")
        print("="*50 + "\n")
        
        try:
            while True:
                # Get voice input
                user_input = await self.process_voice_input()
                if not user_input:
                    print("I didn't catch that. Could you please repeat?")
                    continue
                
                # Generate and speak response
                audio_data = await self.generate_response(user_input)
                if audio_data:
                    self.tts_engine.play_audio(audio_data)
                
        except KeyboardInterrupt:
            print("\nGoodbye!")
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            print(f"An error occurred: {str(e)}")

def main():
    """Main entry point for the voice assistant."""
    # Check for required environment variables
    if not os.getenv("OPENROUTER_API_KEY"):
        print("Error: OPENROUTER_API_KEY environment variable is not set.")
        print("Please create a .env file with your OpenRouter API key.")
        return
    
    # Create and run the assistant
    assistant = VoiceAssistant()
    asyncio.run(assistant.run_conversation_loop())

if __name__ == "__main__":
    main()
