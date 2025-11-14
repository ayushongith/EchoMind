import speech_recognition as sr
import numpy as np
import io
from pydub import AudioSegment
import logging

class STTEngine:
    def __init__(self, model_name="whisper"):
        """
        Initialize the Speech-to-Text engine.
        
        Args:
            model_name (str): STT model to use ('whisper', 'google', or 'vosk')
        """
        self.recognizer = sr.Recognizer()
        self.recognizer.energy_threshold = 300  # Minimum audio energy for speech detection
        self.recognizer.pause_threshold = 0.8   # Seconds of non-speaking audio before a phrase is considered complete
        self.recognizer.non_speaking_duration = 0.5  # Seconds of non-speaking audio to keep on both sides of recording
        self.model_name = model_name
        
        # Configure logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
    
    def audio_to_text(self, audio_data, sample_rate=16000):
        """
        Convert audio data to text.
        
        Args:
            audio_data (numpy.ndarray): Audio data as a numpy array
            sample_rate (int): Sample rate of the audio data
            
        Returns:
            str: Transcribed text, or None if transcription failed
        """
        if audio_data.size == 0:
            self.logger.warning("Empty audio data received for transcription")
            return None
            
        # Convert numpy array to AudioData
        audio_segment = AudioSegment(
            audio_data.tobytes(),
            frame_rate=sample_rate,
            sample_width=audio_data.dtype.itemsize,
            channels=1
        )
        
        # Convert to WAV format expected by SpeechRecognition
        wav_data = io.BytesIO()
        audio_segment.export(wav_data, format="wav")
        wav_data.seek(0)
        
        with sr.AudioFile(wav_data) as source:
            try:
                audio = self.recognizer.record(source)
                
                if self.model_name.lower() == "whisper":
                    text = self.recognizer.recognize_whisper(
                        audio,
                        model="base",  # Can be 'tiny', 'base', 'small', 'medium', or 'large'
                        language="english"
                    )
                elif self.model_name.lower() == "google":
                    text = self.recognizer.recognize_google(audio)
                else:
                    raise ValueError(f"Unsupported STT model: {self.model_name}")
                
                self.logger.info(f"STT Result: {text}")
                return text.strip()
                
            except sr.UnknownValueError:
                self.logger.warning("Speech recognition could not understand audio")
                return None
            except sr.RequestError as e:
                self.logger.error(f"Could not request results from speech recognition service; {e}")
                return None
            except Exception as e:
                self.logger.error(f"Error in speech recognition: {str(e)}")
                return None
    
    def listen_and_transcribe(self, timeout=5, phrase_time_limit=10):
        """
        Listen to microphone and transcribe speech in real-time.
        
        Args:
            timeout (float): Time in seconds to wait for speech before timing out
            phrase_time_limit (float): Maximum time in seconds for a single phrase
            
        Returns:
            str: Transcribed text, or None if no speech was detected
        """
        with sr.Microphone() as source:
            self.logger.info("Listening...")
            try:
                audio = self.recognizer.listen(
                    source,
                    timeout=timeout,
                    phrase_time_limit=phrase_time_limit
                )
                return self.recognize(audio)
            except sr.WaitTimeoutError:
                self.logger.warning("No speech detected")
                return None
    
    def recognize(self, audio):
        """
        Recognize speech from audio data using the configured model.
        
        Args:
            audio: AudioData object from the speech_recognition library
            
        Returns:
            str: Recognized text, or None if recognition failed
        """
        try:
            if self.model_name.lower() == "whisper":
                text = self.recognizer.recognize_whisper(
                    audio,
                    model="base",
                    language="english"
                )
            elif self.model_name.lower() == "google":
                text = self.recognizer.recognize_google(audio)
            else:
                raise ValueError(f"Unsupported STT model: {self.model_name}")
            
            self.logger.info(f"Recognized: {text}")
            return text.strip()
            
        except sr.UnknownValueError:
            self.logger.warning("Speech recognition could not understand audio")
            return None
        except sr.RequestError as e:
            self.logger.error(f"Could not request results from speech recognition service; {e}")
            return None
        except Exception as e:
            self.logger.error(f"Error in speech recognition: {str(e)}")
            return None
