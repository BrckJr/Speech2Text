import os
import whisper
import sounddevice as sd
import soundfile as sf
import threading
import numpy as np
import backend.utils.utils as utils


class RecordingError(Exception):
    """Custom exception for recording errors."""
    pass

class Model:
    """
    The AudioModel class handles real-time audio recording, processing, and transcription.

    This class integrates with the Whisper model for speech-to-text functionality, enabling
    users to record audio, save it to files, and transcribe it using pre-trained models.
    """

    def __init__(self, whisper_model="base", sample_rate=16000):
        """
        Initializes the AudioModel with a Whisper model and a specified sample rate.

        This method loads the selected Whisper model for transcription and initializes
        attributes to manage audio recording and processing.

        Args:
            whisper_model (str): The name of the Whisper model to use (e.g., "base", "large"). Defaults to "base".
            Sample_rate (int): The audio sample rate in Hz. Defaults to 16000.

        Attributes:
            self.transcription_model (whisper.Whisper): The loaded Whisper model for transcription.
            self.is_recording (bool): Indicates whether audio recording is active.
            self.temp_audio_data (list): Buffer for temporarily storing recorded audio data.
            Sample_rate (int): The sample rate for audio recording.
        """

        # The model is running on CPU as Whisper shows problems with running on MPS,
        # and apparently, it is not much faster on MPS.
        self.transcription_model = whisper.load_model(whisper_model)  # Load Whisper model (base size)
        self.is_recording = False
        self.temp_audio_data = []

        # Sample rate for the recording
        self.sample_rate = sample_rate

    def start_recording_audio(self):
        """
        Starts the audio recording process in a separate thread.

        This method initializes an audio input stream, continuously recording audio
        data while `is_recording` is True. Audio processing is managed in real-time
        via the `callback` function. Recording occurs in a separate thread to avoid
        blocking the main program.

        This method resets any previously stored audio data before starting a new recording.

        Raises:
            RuntimeError: If the audio input device is unavailable or improperly configured.
        """

        self.is_recording = True

        def record():
            """
            Records audio data into the input stream while `is_recording` is True.
            """
            with sd.InputStream(callback=self.callback, samplerate=self.sample_rate, channels=1):
                while self.is_recording:
                    sd.sleep(100)  # Keep the stream open while recording

        # Start the recording thread
        threading.Thread(target=record, daemon=True).start()

    def pause_recording_audio(self):
        """
        Pauses the audio recording process.

        This method stops adding new audio data to the recording buffer by setting
        `is_recording` to False. If recording is not active, a warning is printed.

        Raises:
            RuntimeError: If `pause_recording_audio` is called when no recording session is active.
        """

        if self.is_recording:
            self.is_recording = False
            print("Recording paused.")
        else:
            print("Recording is not active. Cannot pause.")

    def stop_recording_audio(self, save_audio):
        """
        Stops the audio recording process and saves the recorded audio to a file.

        This method terminates the recording loop by setting `is_recording` to False.
        It then attempts to save the buffered audio data to a .wav file. If the save
        operation fails (e.g., due to invalid or incomplete audio data), the audio
        data is cleared without being stored.

        Args:
            save_audio (bool): Indicates whether audio data should be saved.

        Returns:
            tuple:
                - str: The file path of the saved audio file, or None if saving failed.
                - bool: True if the file was saved successfully, False otherwise.

        Raises:
            ValueError: If there is an issue with the audio data (e.g., it's invalid or empty).
            RecordingError: If the recording is too short or invalid.
        """

        self.is_recording = False

        # If audio should not be saved, stop and reset temp_audio_data
        if not save_audio:
            self.temp_audio_data = []  # Reset recordings after storing the raw audio file
            return None, False

        # Try to save an audio file but if it is too short, catch the exception
        try:
            # Save the recorded audio data to a file
            if len(self.temp_audio_data) == 0:
                print("RECORDING TOO SHORT")
                raise RecordingError("Recording is too short.")
            filepath = self.save_raw_audio_to_file(self.temp_audio_data)
            self.temp_audio_data = []  # Reset recordings after storing the raw audio file
            return filepath, True
        except RecordingError as e:
            # Catch the custom error for too short recordings
            print(f"Recording error: {e}")
            self.temp_audio_data = []  # Reset recordings
            return None, False
        except ValueError as err:
            # Handle the ValueError exception from save_raw_audio_to_file
            print(f"Error while concatenating audio: {err}")
            self.temp_audio_data = []  # Reset recordings
            return None, False
        except Exception as e:
            # Catch all other exceptions
            print(f"Unexpected error: {e}")
            self.temp_audio_data = []  # Reset recordings
            return None, False

    def callback(self, indata, frames, time, status):
        """
        Callback function for processing audio data in real-time.

        This function is triggered by the audio input stream whenever new audio data is available.
        It appends the audio data to the `temp_audio_data` list while `is_recording` is True.

        Args:
            indata (numpy.ndarray): The audio input data as a NumPy array.
            frames (int): The number of audio frames in `indata`.
            time (CData): Timing information about the input stream (e.g., current time).
            status (sounddevice.CallbackFlags): Status flags indicating errors or warnings during the stream.
        """
        if self.is_recording:
            self.temp_audio_data.append(indata.copy())

    def save_raw_audio_to_file(self, raw_audio):
        """
        Saves raw audio data to a .wav file with a timestamped filename.

        This method concatenates chunks of raw audio data (passed as a list of numpy arrays)
        into a single audio stream, then saves it to a .wav file in the "output/raw_audio"
        directory. The filename is generated with a timestamp to ensure uniqueness.

        If the audio data is invalid (e.g., the list is empty or contains invalid chunks),
        a `ValueError` is raised. If the file cannot be written to disk, an `IOError` is raised.

        Args:
            raw_audio (list of numpy.ndarray): List of raw audio data chunks, where each
                chunk is a NumPy array representing audio samples.

        Returns:
            tuple:
                - str: The file path of the saved .wav file if the save is successful,
                  or None if saving failed.

        Raises:
            ValueError: If the input `raw_audio` list is empty or contains invalid data.
            IOError: If there is an issue writing the .wav file to disk.
        """

        file_path = utils.generate_file_path("raw_audio")

        try:
            # Combine the chunks of raw audio data into a single numpy array
            audio_data = np.concatenate(raw_audio, axis=0)
        except ValueError as err:
            print(f"Error while concatenating audio: {err}")
            return None

        # Save the audio data to the specified .wav file
        try:
            sf.write(file_path, audio_data, self.sample_rate)
            print(f"Audio saved to {file_path}")
            return file_path  # No error, file saved successfully
        except IOError as e:
            print(f"Failed to save audio: {e}")
            return None
        except Exception as e:
            print(f"Unexpected error: {e}")
            return None

    def transcribe_raw_audio(self, filepath):
        """
        Transcribes the raw audio file using the Whisper model.

        This method processes the audio file at the given file path through the Whisper
        model to generate a transcription. The resulting text is saved to a file.

        Args:
            filepath (str): The path to the audio file to transcribe.

        Returns:
            tuple:
                str: The file path of the saved .txt file, or None if saving failed.
                bool: True if the file was saved successfully, False otherwise.

        Raises:
            FileNotFoundError: If the specified audio file is not found.
            RuntimeError: If the transcription process encounters an error.
        """

        result = self.transcription_model.transcribe(audio=filepath)
        transcription = result["text"].strip()  # Clean up any leading/trailing whitespace
        filepath, save_successful = self.save_transcription_to_file(transcription)
        return filepath, save_successful

    @staticmethod
    def save_transcription_to_file(transcription):
        """
        Save the transcribed text to a .txt file with a timestamped filename.

        This method generates a file path for the transcription and writes the transcribed text to it.
        The filename includes a timestamp for uniqueness. If saving fails, an error message is printed.

        Args:
            transcription (str): The transcribed text to save to the file.

        Returns:
            tuple:
                str: The file path of the saved .txt file, or None if saving failed.
                bool: True if the file was saved successfully, False otherwise.
        """
        # Generate the file path for the transcription file
        file_path = utils.generate_file_path("transcription")

        # Save the transcription text to the file
        try:
            with open(file_path, 'w') as file:
                file.write(transcription)
            save_successful = True

            print(f"Transcription saved to {file_path}")
        except Exception as e:
            print(f"Failed to save transcription: {e}")
            return None

        return file_path, save_successful

    @staticmethod
    def delete_all_files(files_to_delete, userID):
        """
        Deleting files in output directory.

        Cleans up the output directory by removing all existing files,
        including all raw audio files and transcriptions for a specific user.

        Args:
            files_to_delete (list of str): The list of audio files to delete for a specific user.
            userID (int): The ID of the user for whom files should be deleted.
        """
        try:
            # Define the base path for static files
            BASE_PATH = 'backend/static'

            # Delete the files contained in the files_to_delete list
            for file in files_to_delete:
                for attribute in ['audio_path', 'transcription_path']:
                    file_path = getattr(file, attribute, None)
                    if file_path:
                        full_path = os.path.join(BASE_PATH, file_path)
                        if os.path.isfile(full_path):
                            os.remove(full_path)
        except Exception as e:
            print(f"Error during cleanup: {e}")
        else:
            print(f"Files of user {userID} deleted successfully.")

