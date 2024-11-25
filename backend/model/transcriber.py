import os
import whisper
import sounddevice as sd
import soundfile as sf
import threading
import numpy as np
import backend.utils.utils as utils

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
            sample_rate (int): The audio sample rate in Hz. Defaults to 16000.

        Attributes:
            transcription_model (whisper.Whisper): The loaded Whisper model for transcription.
            is_recording (bool): Indicates whether audio recording is active.
            temp_audio_data (list): Buffer for temporarily storing recorded audio data.
            sample_rate (int): The sample rate for audio recording.
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

    def stop_recording_audio(self):
        """
        Stops the audio recording process and saves the recorded audio to a file.

        This method terminates the recording loop by setting `is_recording` to False.
        It then saves the buffered audio data to a .wav file. If the save operation fails,
        the audio data is cleared without being stored.

        Returns:
            tuple:
                str: The file path of the saved audio file, or None if saving failed.
                bool: True if the file was saved successfully, False otherwise.

        Raises:
            IOError: If there is an issue saving the file to disk.
        """

        self.is_recording = False

        # Save the recorded audio data to a file
        filepath, save_successful = self.save_raw_audio_to_file(self.temp_audio_data)
        self.temp_audio_data = []  # Reset recordings after storing the raw audio file
        return filepath, save_successful

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

        This method concatenates chunks of raw audio data into a single array and writes
        it to a .wav file in the "output/raw_audio" directory. The filename includes a
        timestamp to ensure uniqueness. If saving fails, an error message is printed.

        Args:
            raw_audio (list of numpy.ndarray): List of raw audio data chunks, where each
                chunk is a NumPy array.

        Returns:
            tuple:
                str: The file path of the saved .wav file, or None if saving failed.
                bool: True if the file was saved successfully, False otherwise.

        Raises:
            ValueError: If the input `raw_audio` list is empty or invalid.
            IOError: If there is an issue writing the file to disk.
        """

        file_path = utils.generate_file_path("raw_audio")
        save_successful = False

        try:
            # Combine the chunks of raw audio data into a single numpy array
            audio_data = np.concatenate(raw_audio, axis=0)
        except ValueError as err:
            return None, save_successful

        # Save the audio data to the specified .wav file
        try:
            sf.write(file_path, audio_data, self.sample_rate)  # Assuming a sample rate of 16kHz
            save_successful = True
            print(f"Audio saved to {file_path}")
        except Exception as e:
            print(f"Failed to save audio: {e}")

        return file_path, save_successful

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
    def delete_all_files():
        """
        Cleans up the output directory by removing all existing files,
        including all raw audio files and transcriptions.
        """
        try:
            # Define the paths to the directories
            raw_audio_dir = 'backend/static/output/raw_audio'
            transcription_dir = 'backend/static/output/transcription'

            # Check if raw_audio directory exists and remove all its contents
            if os.path.exists(raw_audio_dir) and os.path.isdir(raw_audio_dir):
                for filename in os.listdir(raw_audio_dir):
                    file_path = os.path.join(raw_audio_dir, filename)
                    if os.path.isfile(file_path):
                        os.remove(file_path)
                print("Raw audio files cleared.")

            # Check if transcription directory exists and remove all its contents
            if os.path.exists(transcription_dir) and os.path.isdir(transcription_dir):
                for filename in os.listdir(transcription_dir):
                    file_path = os.path.join(transcription_dir, filename)
                    if os.path.isfile(file_path):
                        os.remove(file_path)
                print("Transcription files cleared.")

        except Exception as e:
            print(f"Error during cleanup: {e}")
        else:
            print("All contents from the output directories are cleared.")
