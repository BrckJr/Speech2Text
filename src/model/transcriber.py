import whisper
import src.utils.utils as utils

class RecordingError(Exception):
    """Custom exception for recording errors."""
    pass

class Model:
    """
    The AudioModel class handles transcription of an audio recording.

    This class integrates with the Whisper model for speech-to-text functionality, enabling
    users to transcribe recordings using pre-trained models.
    """

    def __init__(self, whisper_model="base"):
        """
        Initializes the AudioModel with a Whisper model and a specified sample rate.

        Args:
            whisper_model (str): The name of the Whisper model to use (e.g., "base", "large"). Defaults to "base".
        """
        self.transcription_model = whisper.load_model(whisper_model)

    def transcribe_raw_audio(self, audio_filepath):
        """
        Transcribes a raw audio file using the Whisper model and extracts detailed transcription metadata.

        This method processes the given audio file to generate a transcription, extract segments with
        timestamps, and determine language and word count. The transcription is saved to a file, and
        metadata is returned for further analysis.

        Args:
            audio_filepath (str): The full file path of the audio file to transcribe.

        Returns:
            tuple:
                str: The file path where the transcription (.txt) was saved. None if saving failed.
                bool: True if the transcription was saved successfully, False otherwise.
                list[dict]: A list of dictionaries, each representing a transcription segment.
                    Each dictionary includes:
                        - "id" (int): Segment identifier.
                        - "start" (float): Start time of the segment in seconds.
                        - "end" (float): End time of the segment in seconds.
                        - "text" (str): Transcribed text of the segment.
                int: The total number of words in the transcription.
                str: The detected language of the audio recording and transcription.

        Raises:
            FileNotFoundError: If the specified audio file does not exist.
            RuntimeError: If an error occurs during the transcription process.
        """

        # Transcribe the audio including the timestamps to allow analysis in the analytics class
        result = self.transcription_model.transcribe(audio=audio_filepath, word_timestamps=True)

        transcription = result["text"].strip()  # Clean up any leading/trailing whitespace
        language = result["language"] # Get the language from the audio recording / transcription
        word_count = len(transcription.split()) # Count words in the transcription text

        filepath, save_successful = self.save_transcription_to_file(transcription, audio_filepath)

        # Extract segments for analysis purpose
        segments = result.get("segments", [])

        return filepath, save_successful, segments, word_count, language

    @staticmethod
    def save_transcription_to_file(transcription, audio_filepath):
        """
        Saves the transcribed text to a .txt file and returns the file path and status.

        This method generates a file path based on the audio file's name and saves the provided
        transcription text to a .txt file. If the operation is unsuccessful, it handles the error
        gracefully and returns `None` with a failure status.

        Args:
            transcription (str): The transcribed text to be saved.
            audio_filepath (str): The path to the source audio file, used to derive the transcription file name.

        Returns:
            tuple:
                str: The file path of the saved .txt file, or `None` if the saving process failed.
                bool: `True` if the file was saved successfully, `False` otherwise.

        Notes:
            - The transcription file path is generated using the `utils.generate_file_path` method.
            - If an exception occurs during the file-saving process, the method will return `None`
              and avoid raising the exception.
            - The audio file name is extracted and used as the base for the transcription file name.

        Raises:
            None: This method does not raise exceptions but instead returns `None` on failure.
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
