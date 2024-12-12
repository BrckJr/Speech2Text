import whisper
import sounddevice as sd
import soundfile as sf
import threading
import numpy as np
import src.utils.utils as utils

class RecordingError(Exception):
    """Custom exception for recording errors."""
    pass

class Model:
    """
    The AudioModel class handles real-time audio recording, processing, and transcription.

    This class integrates with the Whisper model for speech-to-text functionality, enabling
    users to record audio, save it to files, and transcribe it using pre-trained models.
    """

    def __init__(self, whisper_model="base"):
        """
        Initializes the AudioModel with a Whisper model and a specified sample rate.

        Args:
            whisper_model (str): The name of the Whisper model to use (e.g., "base", "large"). Defaults to "base".
        """
        self.transcription_model = whisper.load_model(whisper_model)

    def transcribe_raw_audio(self, audio_filepath, get_segments):
        """
        Transcribes the raw audio file using the Whisper model.

        This method processes the audio file at the given file path through the Whisper
        model to generate a transcription. The resulting text is saved to a file.

        Args:
            audio_filepath (str): The path to the audio file to transcribe.
            get_segments (bool): Indicates whether the segments are needed (for analysis) or not (for transcription only).

        Returns:
            tuple:
                str: The file path of the saved .txt file, or None if saving failed.
                bool: True if the file was saved successfully, False otherwise.
                list: List of dictionaries with each dictionary representing information about the transcription segment, e.g., the id, start/end time, text, etc.
                int: Number of words in the transcription.
                str: Language of the audio recording and transcription.

        Raises:
            FileNotFoundError: If the specified audio file is not found.
            RuntimeError: If the transcription process encounters an error.
        """

        # Transcribe the audio including the timestamps to allow analysis in the analytics class
        result = self.transcription_model.transcribe(audio=audio_filepath, word_timestamps=True)

        transcription = result["text"].strip()  # Clean up any leading/trailing whitespace
        language = result["language"] # Get the language from the audio recording / transcription
        word_count = len(transcription.split()) # Count words in the transcription text

        filepath, save_successful = self.save_transcription_to_file(transcription, audio_filepath)

        segments = None
        # If segments are needed for analytics, extract them from the transcription result
        if get_segments:
            segments = result.get("segments", [])

        return filepath, save_successful, segments, word_count, language

    @staticmethod
    def save_transcription_to_file(transcription, audio_filepath):
        """
        Save the transcribed text to a .txt file with a timestamped filename.

        This method generates a file path for the transcription and writes the transcribed text to it.
        The filename includes a timestamp for uniqueness. If saving fails, an error message is printed.

        Args:
            transcription (str): The transcribed text to save to the file.
            audio_filepath (str): The path to the audio file to transcribe.

        Returns:
            tuple:
                str: The file path of the saved .txt file, or None if saving failed.
                bool: True if the file was saved successfully, False otherwise.
        """


        # Extract only the filename of the audio recording including timestamp
        audio_filename = audio_filepath.replace('src/static/output/raw_audio/', '')[:-4]
        # Generate the file path for the transcription file
        recording_filepath = utils.generate_file_path("transcription", audio_filename)

        # Save the transcription text to the file
        try:
            with open(recording_filepath, 'w') as file:
                file.write(transcription)
            save_successful = True
        except Exception:
            return None

        return recording_filepath, save_successful
