import whisper
import sounddevice as sd
import numpy as np
import tempfile
from scipy.io.wavfile import write
import time


class AudioModel:
    """
    The AudioModel class is responsible for handling the core functionality of
    recording audio and transcribing it using the Whisper model.

    Attributes:
        model (whisper.model): A Whisper model instance for transcription.
    """

    def __init__(self):
        """
        Initializes the AudioModel by loading the Whisper model.

        The 'base' model of Whisper is loaded by default, but this can be
        adjusted based on the requirements for speed or accuracy.
        """
        self.model = whisper.load_model("base")  # Load Whisper model (base size)

    def record_audio(self, duration=5, sample_rate=16000):
        """
        Records audio from the microphone, saves it temporarily as a WAV file,
        and returns the transcribed text using the Whisper model.

        Args:
            duration (int): The duration in seconds for which to record audio. Default is 5 seconds.
            sample_rate (int): The sample rate for the audio recording. Default is 16000 Hz, which is typical for Whisper.

        Returns:
            str: The transcribed text from the audio.
            None: If there is an error in recording or transcribing, it returns None.

        Raises:
            Exception: Any exception raised during the audio recording or transcription process will be caught
                       and logged, but the method will return None.
        """
        try:
            print("Listening...")
            # Record audio for a set duration (in seconds)
            audio_data = sd.rec(int(duration * sample_rate), samplerate=sample_rate, channels=1, dtype="float32")
            sd.wait()  # Wait until recording is finished

            # Normalize audio data to 16-bit PCM format
            audio_data_int16 = np.int16(audio_data * 32767)

            # Save audio to a temporary WAV file
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_audio_file:
                write(temp_audio_file.name, sample_rate, audio_data_int16)  # Save the WAV file
                temp_audio_file.flush()

                # Use Whisper to transcribe the audio
                result = self.model.transcribe(temp_audio_file.name)
                translated_text = result["text"].strip()  # Clean up any leading/trailing whitespace
                return translated_text
        except Exception as e:
            print(f"Error: {e}")
            return None
