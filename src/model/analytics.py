import os
from datetime import datetime
import wave
import matplotlib
import matplotlib.pyplot as plt
import librosa
from librosa import feature
import numpy as np
from src.utils import utils
from src.model import transformer

matplotlib.use('Agg') # use this to avoid crashes of the program when matplotlib outside the main thread

class Analytics:
    """
    The Analytics class handles the analysis of an audio recording.
    """
    def __init__(self, audio_filepath, transcription_filepath, transcription_segments, word_count, language):
        """
        Initializes the Analytics class.
        """
        self.audio_filepath = audio_filepath # Full file path to the audio file "src/static/output/..."
        self.transcription_filepath = transcription_filepath # Full file path to the transcription file "src/static/output/..."
        self.transcription_segments = transcription_segments # List of tuples with word count per segment
        self.word_count = word_count # Number of words in the audio file
        self.language = language # Language of the audio recording and transcription
        self.no_recording_content = False # Set to true if recording is empty

    def calculate_wpm(self, step_size=1):
        """
        Calculate words per minute (WPM) using a sliding window approach.

        Args:
            step_size (int): Step size for sliding the window in seconds.

        Returns:
            list: A list of tuples (time, wpm) for each window position.
                  The time represents the center of the window.
        """
        if not self.transcription_segments:
            return []

        def get_window_length():
            # Set interval length depending on the audio length
            audio_length = self.get_wav_length()
            if audio_length < 60:
                return 5  # Short recordings
            elif audio_length < 600:
                return 15  # Medium recordings
            elif audio_length < 1800:
                return 30  # Long recordings
            else:
                return 60  # Very long recordings

        window_length = get_window_length()

        total_audio_length = self.get_wav_length()
        time_wpm = []
        current_time = 0

        while current_time + window_length <= total_audio_length:
            # Define the current window range
            window_start = current_time
            window_end = current_time + window_length
            window_center = (window_start + window_end) / 2  # Timestamp for x-axis
            words_in_window = []

            for segment in self.transcription_segments:
                # Check if segment overlaps with the window
                if segment["end"] >= window_start and segment["start"] <= window_end:
                    # Calculate overlap duration
                    segment_start = max(segment["start"], window_start)
                    segment_end = min(segment["end"], window_end)
                    overlap_duration = segment_end - segment_start

                    # Estimate number of words in the overlap
                    total_segment_duration = segment["end"] - segment["start"]
                    if total_segment_duration > 0:
                        words = segment["text"].split()
                        words_in_overlap = int(len(words) * (overlap_duration / total_segment_duration))
                        words_in_window.extend(words[:words_in_overlap])

            # Calculate WPM for the current window
            wpm = (len(words_in_window) / window_length) * 60
            time_wpm.append((window_center, wpm))  # Use window_center for the timestamp

            # Move the window forward
            current_time += step_size

        return time_wpm

    def generate_plot_wpm(self):
        """
        Plot the WPM over time and store the generated graphic in the output/speed_graphics directory.

        Returns:
            str: Path to the stored speech speed graphic
        """
        # Extract only the filename of the audio recording including timestamp
        audio_filename = self.audio_filepath.replace('src/static/output/raw_audio/', '')[:-4]
        # Generate the file path for the transcription file
        speed_graphics_filepath = utils.generate_file_path("speed_graphics", audio_filename)

        time_wpm = self.calculate_wpm()

        times, wpms = zip(*time_wpm) if time_wpm else ([], [])

        # If no valid data, handle gracefully with a placeholder
        if not times or not wpms:
            self.no_recording_content = True
            plt.figure()
            plt.text(0.5, 0.5, 'No WPM data to display', ha='center', va='center', fontsize=12, color='#f1f1f1')
            plt.axis('off')
            plt.savefig(speed_graphics_filepath, format="png", dpi=300, transparent=True)
            plt.close()
            return speed_graphics_filepath

        # Add red shadow regions on the y-axis (y=50 to 100 and y=200 to 250)
        plt.axhspan(200, 250, color='red', alpha=0.1)
        plt.axhspan(50, 100, color='red', alpha=0.1)

        # Add green shadow regions on the y-axis (y=50 to 100 and y=200 to 250)
        plt.axhspan(100, 200, color='green', alpha=0.1)

        # Adding dots at the actual data points
        # plt.scatter(times, wpms, color='#f1f1f1', linewidth=2)

        # Connecting the points with lines and applying the color scheme
        plt.plot(times, wpms, color='#f1f1f1', linewidth=2)

        # Set x-axis and y-axis limits
        plt.ylim(50, 250)
        plt.xlim(0, self.get_wav_length())

        # Add labels, grid, and legend
        plt.xlabel("Time (seconds)", fontsize=12, fontweight='bold', color='#f1f1f1')
        plt.ylabel("Words per Minute", fontsize=12, fontweight='bold', color='#f1f1f1')
        plt.grid(True, color='#f1f1f1')

        # Make the outer frame bolder and white
        ax = plt.gca()  # Get current axes
        for spine in ax.spines.values():
            spine.set_visible(True)
            spine.set_linewidth(2)  # Make the frame bolder
            spine.set_color('#f1f1f1')  # Set frame color to white

        # Adjust the size and weight of tick labels (numbers on the axes)
        plt.tick_params(axis='both', which='major', labelsize=10, width=2,
                        colors='#f1f1f1')  # Tick marks and labels in white
        plt.xticks(fontsize=10, fontweight='bold', color='#f1f1f1')  # Specifically for x-axis numbers
        plt.yticks(fontsize=10, fontweight='bold', color='#f1f1f1')  # Specifically for y-axis numbers

        plt.title("Speaking Speed Over Time", fontsize=14, fontweight='bold', color='#f1f1f1')

        # Save the plot
        plt.savefig(speed_graphics_filepath, format="png", dpi=300, transparent=True)

        plt.close()

        return speed_graphics_filepath

    def analyze_pitch(self):
        """
        Analyze pitch (fundamental frequency) and generate a pitch contour plot.

        Returns:
            float: Mean of the pitch
            float: Standard deviation of the pitch
            float: Range of the pitch frequencies
            str: filepath to the plot of the pitch contour
        """

        # Extract only the filename of the audio recording including timestamp
        audio_filename = self.audio_filepath.replace('src/static/output/raw_audio/', '')[:-4]
        # Generate the file path for the transcription file
        pitch_graphics_filepath = utils.generate_file_path("pitch_graphics", audio_filename)

        # Load the audio signal
        y, sr = librosa.load(self.audio_filepath)
        # Estimate pitch using librosa's pyin
        # f0: fundamental frequency over time
        # voiced_flag: whether each time frame contains speech
        f0, voiced_flag, voiced_time = librosa.pyin(y, fmin=50, fmax=600, sr=16000)

        # Remove invalid pitch intervals (non-voiced or silence areas)
        time = np.linspace(0, len(y) / sr, len(f0))  # Time values corresponding to each frame
        valid_indices = voiced_flag & (f0 > 0)  # Only take voiced intervals with a valid pitch
        filtered_time = time[valid_indices]
        filtered_f0 = f0[valid_indices]

        # If no valid pitch data is detected, replace filtered_f0 with an empty NumPy array
        if filtered_f0.size == 0:
            filtered_time = np.array([])  # Convert to an empty NumPy array
            filtered_f0 = np.array([])  # Convert to an empty NumPy array

        # Create summary statistics for the pitch only if valid data exists
        mean_pitch = np.mean(filtered_f0) if filtered_f0.size > 0 else 0
        std_pitch = np.std(filtered_f0) if filtered_f0.size > 0 else 0
        min_pitch = np.min(filtered_f0) if filtered_f0.size > 0 else 0
        max_pitch = np.max(filtered_f0) if filtered_f0.size > 0 else 0
        pitch_range = max_pitch - min_pitch


        # Plotting the pitch analysis graph only if there is data to plot
        if filtered_time.size > 0 and filtered_f0.size > 0 and not self.no_recording_content:
            plt.plot(filtered_time, filtered_f0, color='#f1f1f1', linewidth=2)

            # Set x-axis and y-axis limits
            plt.ylim(0, np.max(filtered_f0) * 1.1)
            plt.xlim(0, self.get_wav_length()*1.1)

            # Update labels and grid with consistent custom colors
            plt.xlabel("Time (seconds)", fontsize=12, fontweight='bold', color='#f1f1f1')
            plt.ylabel("Pitch (Hz)", fontsize=12, fontweight='bold', color='#f1f1f1')
            plt.grid(True, color='#f1f1f1')

            # Make the outer frame bolder and white
            ax = plt.gca()  # Get current axes
            for spine in ax.spines.values():
                spine.set_visible(True)
                spine.set_linewidth(2)  # Make the frame bolder
                spine.set_color('#f1f1f1')  # Set frame color to white

            # Adjust the size and weight of tick labels (numbers on the axes)
            plt.tick_params(axis='both', which='major', labelsize=10, width=2,
                            colors='#f1f1f1')  # Tick marks and labels in white
            plt.xticks(fontsize=10, fontweight='bold', color='#f1f1f1')  # Specifically for x-axis numbers
            plt.yticks(fontsize=10, fontweight='bold', color='#f1f1f1')  # Specifically for y-axis numbers

            plt.title("Pitch Over Time", fontsize=14, fontweight='bold', color='#f1f1f1')
        else:
            # No data to plot
            plt.figure()
            plt.text(0.5, 0.5, 'No pitch data to display', ha='center', va='center', fontsize=12, color='#f1f1f1')
            plt.axis('off')  # Turn off the axes when no data is available


        # Save the plot
        plt.savefig(pitch_graphics_filepath, format="png", dpi=300, transparent=True)
        plt.close()

        return mean_pitch, std_pitch, pitch_range, pitch_graphics_filepath

    def get_general_info(self):
        """
        This method returns general information about the recorded audio file

        For the given audio file, this method returns information about language, length,
        topic, recording date and time, count of words, etc.


        Returns:
            tuple:
                - str: an AI generated title for the recording.
                - str: the language used in the recording.
                - float: length of the recording in format seconds
                - datetime: Date and time when the audio was recorded.
                - int: count of words in the recording
        """


        def get_file_creation_time(filepath):
            # Returns datetime object of the file creation time
            creation_time = os.path.getctime(filepath)
            return datetime.fromtimestamp(creation_time)  # Return complete datetime object

        audio_length = self.get_wav_length()
        saving_date_and_time = get_file_creation_time(self.audio_filepath)

        # Check the length of transcription and return transcription itself if to few words
        if self.word_count < 10:
            # When the text only contains less than 20 words, return text itself
            with open(self.transcription_filepath, 'r') as file:
                title = file.read()
        else:
            # Get title from the transformer model
            title = transformer.generate_summary(self.transcription_filepath, 5, 10)

        return title, self.language, audio_length, saving_date_and_time, self.word_count

    def get_summary(self):
        """
        This method returns a summary of the recorded audio file.

        The length of the summary is depending on the length of the recorded audio file.

        Returns:
            - str: an AI generated summary for the recording.
        """

        if self.word_count < 20:
            # When the text only contains less than 20 words, return text itself
            with open(self.transcription_filepath, 'r') as file:
                text = file.read()
            return text
        elif self.word_count < 100:
            max_length = 30
            min_length = 10
        elif self.word_count < 300:
            max_length = 60
            min_length = 20
        elif self.word_count < 500:
            max_length = 100
            min_length = 40
        else:
            max_length = 150
            min_length = 50

        # Get summary from the transformer model
        summary = transformer.generate_summary(self.transcription_filepath, min_length, max_length)

        return summary

    def get_wav_length(self):
        """
        This method returns the length of the audio file from the filepath
        """
        with wave.open(self.audio_filepath, 'rb') as wav_file:
            frames = wav_file.getnframes()
            rate = wav_file.getframerate()
            duration = frames / float(rate)
        return duration

    def analyze_energy(self):
        """
        Analyze the energy of the audio signal and generate an energy plot.

        The energy is normalized such that the maximum energy level is 1.

        Returns:
            float: Average energy of the audio (normalized).
            float: Standard deviation of the energy (normalized).
            str: Path to the energy plot.
        """
        # Extract only the filename of the audio recording including timestamp
        audio_filename = self.audio_filepath.replace('src/static/output/raw_audio/', '')[:-4]
        # Generate the file path for the energy plot
        energy_graphics_filepath = utils.generate_file_path("energy_graphics", audio_filename)

        # Load the audio signal
        y, sr = librosa.load(self.audio_filepath)

        # Calculate the short-time energy (RMS)
        frame_length = 2048
        hop_length = 512
        rms_energy = librosa.feature.rms(y=y, frame_length=frame_length, hop_length=hop_length)[0]
        times = librosa.frames_to_time(np.arange(len(rms_energy)), sr=sr, hop_length=hop_length)

        # Normalize the energy values to have a maximum of 1
        normalized_rms_energy = rms_energy / np.max(rms_energy) if np.max(rms_energy) > 0 else rms_energy

        # Compute statistics
        average_energy = np.mean(normalized_rms_energy)
        std_energy = np.std(normalized_rms_energy)

        if not self.no_recording_content:
            # Plot the energy graph
            plt.figure()
            plt.plot(times, normalized_rms_energy, color='#f1f1f1', linewidth=2)

            # Update labels and grid with consistent custom colors
            plt.xlabel("Time (seconds)", fontsize=12, fontweight='bold', color='#f1f1f1')
            plt.ylabel("Relative Energy", fontsize=12, fontweight='bold', color='#f1f1f1')
            plt.grid(True, color='#f1f1f1')

            # Make the outer frame bolder and white
            ax = plt.gca()  # Get current axes
            for spine in ax.spines.values():
                spine.set_visible(True)
                spine.set_linewidth(2)  # Make the frame bolder
                spine.set_color('#f1f1f1')  # Set frame color to white

            # Adjust the size and weight of tick labels (numbers on the axes)
            plt.tick_params(axis='both', which='major', labelsize=10, width=2, colors='#f1f1f1')
            plt.xticks(fontsize=10, fontweight='bold', color='#f1f1f1')  # Specifically for x-axis numbers
            plt.yticks(fontsize=10, fontweight='bold', color='#f1f1f1')  # Specifically for y-axis numbers

            plt.title("Normalized Energy Over Time", fontsize=14, fontweight='bold', color='#f1f1f1')
        else:
            # No data to plot
            plt.figure()
            plt.text(0.5, 0.5, 'No pitch data to display', ha='center', va='center', fontsize=12, color='#f1f1f1')
            plt.axis('off')  # Turn off the axes when no data is available

        # Save the plot
        plt.savefig(energy_graphics_filepath, format="png", dpi=300, transparent=True)
        plt.close()

        return average_energy, std_energy, energy_graphics_filepath

    def improve_text(self):
        """
        Improves grammar, clarity, and readability.

        Returns:
            str: Improved text for the speech
            bool: True if save was successful, False otherwise
        """
        save_successful = False

        # Extract only the filename of the audio recording including timestamp
        audio_filename = self.audio_filepath.replace('src/static/output/raw_audio/', '')[:-4]
        # Generate the file path for the energy plot
        improved_text_filepath = utils.generate_file_path("improved_text", audio_filename)

        try:
            improved_text = transformer.improve_text(self.transcription_filepath)
        except Exception as e:
            improved_text = f"Model was not able to improved text because of following error: {str(e)}"

        # Save the improved text to the file
        try:
            with open(improved_text_filepath, 'w') as file:
                file.write(improved_text)
            save_successful = True
        except Exception:
            return None

        return improved_text_filepath, save_successful


