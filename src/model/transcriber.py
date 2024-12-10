import os
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

    def __init__(self, whisper_model="base", sample_rate=16000):
        """
        Initializes the AudioModel with a Whisper model and a specified sample rate.

        Args:
            whisper_model (str): The name of the Whisper model to use (e.g., "base", "large"). Defaults to "base".
            sample_rate (int): The audio sample rate in Hz. Default to 16'000.
        """
        self.transcription_model = whisper.load_model(whisper_model)
        self.is_recording = False
        self.temp_audio_data = []
        self.sample_rate = sample_rate
        self.current_device = sd.default.device
        self.device_monitor_thread = threading.Thread(target=self.monitor_devices, daemon=True)
        self.device_monitor_thread.start()

    def start_recording_audio(self):
        """
        Starts the audio recording process in a separate thread.
        """
        self.is_recording = True

        def record():
            while self.is_recording:
                try:
                    with sd.InputStream(callback=self.callback, samplerate=self.sample_rate, channels=1):
                        while self.is_recording:
                            sd.sleep(100)
                except Exception as e:
                    print(f"Error during recording: {e}")
                    self.handle_device_change()

        threading.Thread(target=record, daemon=True).start()

    def pause_recording_audio(self):
        """
        Pauses the audio recording process.
        """
        if self.is_recording:
            self.is_recording = False
            print("Recording paused.")
        else:
            print("Recording is not active. Cannot pause.")

    def stop_recording_audio(self, save_audio, filename=None):
        """
        Stops the audio recording process and optionally saves the audio data.

        Args:
            save_audio (bool): Indicates whether audio data should be saved.
            filename (str): The name of the audio file.

        Returns:
            tuple: (file path of saved audio, success flag)
        """
        self.is_recording = False

        if not save_audio:
            self.temp_audio_data = []
            return None, False

        try:
            if len(self.temp_audio_data) == 0:
                raise RecordingError("Recording is too short.")
            filepath = self.save_raw_audio_to_file(self.temp_audio_data, filename)
            self.temp_audio_data = []
            return filepath, True
        except Exception:
            self.temp_audio_data = []
            return None, False

    def callback(self, indata, frames, time, status):
        """
        Callback function for processing audio data in real-time.
        """
        if self.is_recording:
            self.temp_audio_data.append(indata.copy())

    def monitor_devices(self):
        """
        Monitors audio devices for changes and handles updates dynamically.
        """
        initial_devices = sd.query_devices()
        while True:
            current_devices = sd.query_devices()
            if current_devices != initial_devices:
                print("Audio devices changed! Attempting to recover...")
                self.handle_device_change()
                initial_devices = current_devices
            sd.sleep(1000)

    def handle_device_change(self):
        """
        Handles recovery after an audio device change.
        """
        try:
            self.current_device = sd.default.device
            print(f"Switching to device: {self.current_device}")
            if self.is_recording:
                self.start_recording_audio()
        except Exception as e:
            print(f"Failed to handle device change: {e}")


    def save_raw_audio_to_file(self, raw_audio, filename):
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
            filename (str): The name of the audio file.

        Returns:
            tuple:
                - str: The file path of the saved .wav file if the save is successful,
                  or None if saving failed.

        Raises:
            ValueError: If the input `raw_audio` list is empty or contains invalid data.
            IOError: If there is an issue writing the .wav file to disk.
        """

        # Get filepath for the new audio file
        audio_filepath = utils.generate_file_path("raw_audio", filename)
        try:
            # Combine the chunks of raw audio data into a single numpy array
            audio_data = np.concatenate(raw_audio, axis=0)
        except ValueError:
            return None

        # Save the audio data to the specified .wav file
        try:
            sf.write(audio_filepath, audio_data, self.sample_rate)
            return audio_filepath
        except Exception:
            return None

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
