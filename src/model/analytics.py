import os
from datetime import datetime
import wave
import matplotlib
import matplotlib.pyplot as plt
import librosa
import numpy as np
from scipy.interpolate import interp1d
from src.utils import utils
from src.model import transformer

matplotlib.use('Agg') # use this to avoid crashes of the program when matplotlib outside the main thread

class Analytics:
    """
    The Analytics class handles the analysis of an audio recording.
    """
    def __init__(self, audio_filepath, recording_filepath, transcription_segments, word_count, language):
        """
        Initializes the Analytics class.
        """
        self.audio_filepath = audio_filepath # Full file path to the audio file "src/static/output/..."
        self.recording_filepath = recording_filepath # Full file path to the transcription file "src/static/output/..."
        self.transcription_segments = transcription_segments # List of tuples with word count per segment
        self.word_count = word_count # Number of words in the audio file
        self.language = language # Language of the audio recording and transcription

    def calculate_wpm(self, interval=5):
        """
        Calculate words per minute (WPM) from Whisper transcription segments.

        Args:
            interval (int): Time interval in seconds for WPM calculation.

        Returns:
            list: A list of tuples (time, wpm) for each interval.
        """
        if not self.transcription_segments:
            return []

        time_wpm = []
        current_time = 0
        current_words = []

        for segment in self.transcription_segments:
            start = segment["start"]
            end = segment["end"]
            words = segment["text"].split()

            # Add words to the current interval
            current_words.extend(words)
            # Check if we've passed the current interval
            while start >= current_time + interval:
                # Calculate WPM for the interval
                wpm = (len(current_words) / interval) * 60
                time_wpm.append((current_time, wpm))
                current_words = []  # Reset for the next interval
                current_time += interval

        # Process any remaining words at the end
        if current_words:
            wpm = (len(current_words) / interval) * 60
            time_wpm.append((current_time, wpm))

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

        # Connecting the points with lines and applying the color scheme
        plt.plot(times, wpms, color='#f1f1f1', linewidth=2)

        # Set y-axis limits
        plt.ylim(50, 250)

        # Add labels, grid, and legend
        plt.xlabel("Time (seconds)", fontsize=12, fontweight='bold', color='#f1f1f1')
        plt.ylabel("WPM", fontsize=12, fontweight='bold', color='#f1f1f1')
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

        print(f"Filtered F0 {filtered_f0}, Filtered Time: {filtered_time}")

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
        if filtered_time.size > 0 and filtered_f0.size > 0:
            plt.plot(filtered_time, filtered_f0, color='#f1f1f1', linewidth=2)

            # Set axis limits safely
            plt.ylim(0, np.max(filtered_f0) * 1.1)

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

            plt.title("Pitch Analysis Over Time", fontsize=14, fontweight='bold', color='#f1f1f1')
        else:
            # No data to plot
            plt.figure()
            plt.text(0.5, 0.5, 'No pitch data to display', ha='center', va='center', fontsize=12, color='#f1f1f1')
            plt.axis('off')  # Turn off the axes when no data is available


        # Save the plot
        plt.savefig(pitch_graphics_filepath, format="png", dpi=300, transparent=True)
        plt.close()

        print("Pitch statistics computed successfully.")
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

        def get_wav_length(filepath):
            # returns length of the audio file from the filepath
            with wave.open(filepath, 'rb') as wav_file:
                frames = wav_file.getnframes()
                rate = wav_file.getframerate()
                duration = frames / float(rate)
            return duration

        def get_file_creation_time(filepath):
            # Returns datetime object of the file creation time
            creation_time = os.path.getctime(filepath)
            return datetime.fromtimestamp(creation_time)  # Return complete datetime object

        audio_length = get_wav_length(self.audio_filepath)
        saving_date_and_time = get_file_creation_time(self.audio_filepath)

        # Check the length of transcription and return transcription itself if to few words
        if self.word_count < 10:
            # When the text only contains less than 20 words, return text itself
            with open(self.recording_filepath, 'r') as file:
                title = file.read()
        else:
            # Get title from the transformer model
            title = transformer.generate_summary(self.recording_filepath, 5, 10)

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
            with open(self.recording_filepath, 'r') as file:
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
        summary = transformer.generate_summary(self.recording_filepath, min_length, max_length)

        return summary