import os
import io
import logging
import numpy as np
from gtts import gTTS
import edge_tts
import asyncio
from pydub import AudioSegment
from pydub.playback import play
import tempfile
from typing import Optional, Union, BinaryIO
import wave
import json

class TTSEngine:
    """
    Text-to-Speech engine supporting multiple backends.
    """
    def __init__(self, engine: str = "gtts", voice: str = "en-US-AriaNeural"):
        """
        Initialize the TTS engine.
        
        Args:
            engine (str): TTS engine to use ('gtts' or 'edge')
            voice (str): Voice to use (only for edge-tts)
        """
        self.engine = engine.lower()
        self.voice = voice
        self.logger = logging.getLogger(__name__)
        
    async def text_to_speech_async(self, text: str) -> Optional[bytes]:
        """
        Convert text to speech asynchronously.
        
        Args:
            text (str): Text to convert to speech
            
        Returns:
            Optional[bytes]: Audio data in WAV format, or None if conversion failed
        """
        if self.engine == "edge":
            return await self._edge_tts_convert(text)
        else:
            return self._gtts_convert(text)
    
    def text_to_speech(self, text: str) -> Optional[bytes]:
        """
        Convert text to speech (synchronous wrapper).
        
        Args:
            text (str): Text to convert to speech
            
        Returns:
            Optional[bytes]: Audio data in WAV format, or None if conversion failed
        """
        try:
            if self.engine == "edge":
                return asyncio.run(self._edge_tts_convert(text))
            else:
                return self._gtts_convert(text)
        except Exception as e:
            self.logger.error(f"Error in text_to_speech: {str(e)}")
            return None
            
    def _gtts_convert(self, text: str) -> Optional[bytes]:
        """
        Convert text to speech using gTTS.
        
        Args:
            text (str): Text to convert
            
        Returns:
            Optional[bytes]: Audio data in WAV format, or None if conversion failed
        """
        try:
            # Create a temporary file to store the MP3
            with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as temp_mp3:
                temp_mp3_path = temp_mp3.name
            
            # Generate speech using gTTS
            tts = gTTS(text=text, lang='en', slow=False)
            tts.save(temp_mp3_path)
            
            # Convert MP3 to WAV
            audio = AudioSegment.from_mp3(temp_mp3_path)
            
            # Create a WAV file in memory
            wav_io = io.BytesIO()
            audio.export(wav_io, format='wav')
            wav_data = wav_io.getvalue()
            
            # Clean up temporary file
            os.unlink(temp_mp3_path)
            
            return wav_data
            
        except Exception as e:
            self.logger.error(f"gTTS conversion error: {str(e)}")
            if 'temp_mp3_path' in locals() and os.path.exists(temp_mp3_path):
                os.unlink(temp_mp3_path)
            return None
    
    async def _edge_tts_convert(self, text: str) -> Optional[bytes]:
        """
        Convert text to speech using Edge-TTS.
        
        Args:
            text (str): Text to convert
            
        Returns:
            Optional[bytes]: Audio data in WAV format, or None if conversion failed
        """
        try:
            # Create a temporary file to store the WAV
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_wav:
                temp_wav_path = temp_wav.name
            
            # Generate speech using Edge-TTS
            communicate = edge_tts.Communicate(text, self.voice)
            await communicate.save(temp_wav_path)
            
            # Read the WAV file
            with open(temp_wav_path, 'rb') as f:
                wav_data = f.read()
            
            # Clean up temporary file
            os.unlink(temp_wav_path)
            
            return wav_data
            
        except Exception as e:
            self.logger.error(f"Edge-TTS conversion error: {str(e)}")
            if 'temp_wav_path' in locals() and os.path.exists(temp_wav_path):
                os.unlink(temp_wav_path)
            return None
    
    def save_audio(self, audio_data: bytes, file_path: str) -> bool:
        """
        Save audio data to a file.
        
        Args:
            audio_data (bytes): Audio data in WAV format
            file_path (str): Path to save the audio file
            
        Returns:
            bool: True if save was successful, False otherwise
        """
        try:
            with open(file_path, 'wb') as f:
                f.write(audio_data)
            return True
        except Exception as e:
            self.logger.error(f"Error saving audio file: {str(e)}")
            return False
    
    def play_audio(self, audio_data: bytes) -> bool:
        """
        Play audio data.
        
        Args:
            audio_data (bytes): Audio data in WAV format
            
        Returns:
            bool: True if playback was successful, False otherwise
        """
        try:
            # Create an in-memory file-like object
            audio_io = io.BytesIO(audio_data)
            
            # Load the audio data
            audio = AudioSegment.from_wav(audio_io)
            
            # Play the audio
            play(audio)
            return True
            
        except Exception as e:
            self.logger.error(f"Error playing audio: {str(e)}")
            return False

# Example usage
if __name__ == "__main__":
    # Set up logging
    logging.basicConfig(level=logging.INFO)
    
    # Example 1: Using gTTS
    print("Testing gTTS...")
    tts_gtts = TTSEngine(engine="gtts")
    audio_data = tts_gtts.text_to_speech("Hello, this is a test using gTTS.")
    if audio_data:
        tts_gtts.save_audio(audio_data, "output_gtts.wav")
        print("Saved to output_gtts.wav")
    
    # Example 2: Using Edge-TTS
    print("\nTesting Edge-TTS...")
    tts_edge = TTSEngine(engine="edge", voice="en-US-AriaNeural")
    audio_data = tts_edge.text_to_speech("Hello, this is a test using Edge-TTS.")
    if audio_data:
        tts_edge.save_audio(audio_data, "output_edge.wav")
        print("Saved to output_edge.wav")
