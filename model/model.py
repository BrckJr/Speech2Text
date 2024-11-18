import whisper
import sounddevice as sd
import soundfile as sf
import threading
import numpy as np
import utils.utils as utils


class AudioModel:
    """
    The AudioModel class handles the audio recording process and integrates with
    the Whisper model for speech-to-text functionality.

    This class manages recording audio in real-time, storing the audio data in
    memory, and providing callbacks for audio processing.
    """

    def __init__(self, whisper_model="base", sample_rate=16000):
        """
        Initializes the AudioModel with the specified Whisper model and sample rate.

        This sets up the Whisper model for speech-to-text processing and initializes attributes
        for managing audio recording, including the sample rate for recording.

        Args:
            whisper_model (str): The name of the Whisper model to use (e.g., "base", "large").
            sample_rate (int): The sample rate for audio recording (default is 16000 Hz).
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

        This method opens an audio input stream, continuously records audio data while `is_recording`
        is set to True, and processes audio in real-time through the callback function. The recording
        occurs in a separate thread to prevent blocking the main program.

        This method will reset any previous audio data before starting the recording.

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

        This method temporarily stops adding new audio data to the recording buffer
        by setting `is_recording` to False but keeps the audio stream alive for potential resumption.
        """
        if self.is_recording:
            self.is_recording = False
            print("Recording paused.")
        else:
            print("Recording is not active. Cannot pause.")

    def stop_recording_audio(self):
        """
        Stops the audio recording process and saves the recorded audio to a file.

        This method sets `is_recording` to False, terminating the recording loop, and saves the
        recorded audio data to a .wav file. The file path of the saved audio is returned.

        Returns:
            str: The file path where the recorded audio was saved.
            bool: True if the saving was successful, False otherwise.
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
        Save raw audio data to a .wav file with a timestamped filename.

        This method concatenates raw audio chunks into a single audio array and saves it to a .wav
        file in the "output/raw_audio" directory. The filename includes a timestamp for uniqueness.
        If saving fails, an error message is printed.

        Args:
            raw_audio (list of numpy.ndarray): A list of raw audio data chunks, each represented as
                a numpy array. These chunks are concatenated before saving.

        Returns:
            str: The full file path where the audio file is saved.
            bool: True if the saving was successful, False otherwise.

        Raises:
            Exception: If there is an error during file saving, an exception message is printed.
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
        Transcribes the raw audio file using the selected model.

        This transcribes the audio from the given file path.
        After transcription, it saves the transcribed text to a file.

        Args:
            filepath (str): The path to the audio file to be transcribed.

        """
        result = self.transcription_model.transcribe(audio=filepath)
        transcription = result["text"].strip()  # Clean up any leading/trailing whitespace
        self.save_transcription_to_file(transcription)

    @staticmethod
    def save_transcription_to_file(transcription):
        """
        Save the transcribed text to a .txt file with a timestamped filename.

        This method generates a file path for the transcription and writes the transcribed text to it.
        The filename includes a timestamp for uniqueness. If saving fails, an error message is printed.

        Args:
            transcription (str): The transcribed text to save to the file.

        Returns:
            str: The file path where the transcription was saved.
        """
        # Generate the file path for the transcription file
        file_path = utils.generate_file_path("transcription")

        # Save the transcription text to the file
        try:
            with open(file_path, 'w') as file:
                file.write(transcription)
            print(f"Transcription saved to {file_path}")
        except Exception as e:
            print(f"Failed to save transcription: {e}")
            return None

        return file_path