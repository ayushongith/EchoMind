import pyaudio
import numpy as np
import webrtcvad
from collections import deque
import time

class AudioCapture:
    def __init__(self, sample_rate=16000, chunk_size=1024, channels=1, format=pyaudio.paInt16):
        """
        Initialize the audio capture with specified parameters.
        
        Args:
            sample_rate (int): Audio sample rate in Hz
            chunk_size (int): Number of audio frames per buffer
            channels (int): Number of audio channels (1 for mono, 2 for stereo)
            format: Audio format (default: 16-bit PCM)
        """
        self.sample_rate = sample_rate
        self.chunk_size = chunk_size
        self.channels = channels
        self.format = format
        self.audio = pyaudio.PyAudio()
        self.stream = None
        self.vad = webrtcvad.Vad(3)  # Aggressiveness mode (0-3)
        self.audio_buffer = deque(maxlen=sample_rate * 5)  # 5 second buffer
        
    def start(self):
        """Start the audio stream."""
        self.stream = self.audio.open(
            format=self.format,
            channels=self.channels,
            rate=self.sample_rate,
            input=True,
            frames_per_buffer=self.chunk_size,
            stream_callback=self._callback
        )
        return self
    
    def stop(self):
        """Stop the audio stream and clean up."""
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
        self.audio.terminate()
    
    def _callback(self, in_data, frame_count, time_info, status):
        """Callback function for audio stream."""
        audio_data = np.frombuffer(in_data, dtype=np.int16)
        self.audio_buffer.extend(audio_data)
        return (in_data, pyaudio.paContinue)
    
    def get_audio_chunk(self):
        """Get the next chunk of audio data."""
        if not self.stream or not self.stream.is_active():
            return None
        
        # Get audio data from buffer
        if len(self.audio_buffer) >= self.chunk_size:
            return np.array([self.audio_buffer.popleft() for _ in range(self.chunk_size)])
        return None
    
    def is_speech(self, audio_chunk):
        """Detect if the audio chunk contains speech using WebRTC VAD."""
        if audio_chunk is None or len(audio_chunk) < 480:  # 30ms of 16kHz audio
            return False
        return self.vad.is_speech(audio_chunk.tobytes(), self.sample_rate)
    
    def record_until_silence(self, silence_duration=1.0, chunk_duration=0.1):
        """
        Record audio until silence is detected.
        
        Args:
            silence_duration (float): Duration of silence (in seconds) to stop recording
            chunk_duration (float): Duration of each chunk to process (in seconds)
            
        Returns:
            numpy.ndarray: Recorded audio data
        """
        chunk_size = int(self.sample_rate * chunk_duration)
        silence_threshold = int(silence_duration / chunk_duration)
        silent_chunks = 0
        audio_frames = []
        
        try:
            print("Listening... (speak now)")
            while silent_chunks < silence_threshold:
                chunk = self.get_audio_chunk()
                if chunk is not None:
                    if self.is_speech(chunk):
                        audio_frames.append(chunk)
                        silent_chunks = 0
                        print(".", end="", flush=True)
                    else:
                        if len(audio_frames) > 0:  # Only count silence after speech started
                            silent_chunks += 1
                    
                    # Maintain a reasonable buffer size
                    if len(audio_frames) > 30:  # ~3 seconds at 100ms chunks
                        audio_frames.pop(0)
                
                time.sleep(chunk_duration / 2)  # Small delay to prevent busy waiting
                
        except KeyboardInterrupt:
            print("\nRecording stopped by user")
        
        print("\nFinished recording")
        return np.concatenate(audio_frames) if audio_frames else np.array([])

    def __enter__(self):
        """Context manager entry."""
        self.start()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.stop()
