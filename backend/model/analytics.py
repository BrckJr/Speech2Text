import matplotlib.pyplot as plt


class Analytics:
    """
    The Analytics class handles the analysis of an audio recording.
    """
    def __init__(self, audio_file_path, recording_file_path):
        """
        Initializes the Analytics class.
        """


    @staticmethod
    def calculate_wpm(transcription_segments, interval=5):
        """
        Calculate words per minute (WPM) from Whisper transcription segments.

        Args:
            transcription_segments (list): List of transcription segments with start/end times and text.
            interval (int): Time interval in seconds for WPM calculation.

        Returns:
            list: A list of tuples (time, wpm) for each interval.
        """
        if not transcription_segments:
            raise ValueError("No transcription segments provided.")

        time_wpm = []
        current_time = 0
        current_words = []

        for segment in transcription_segments:
            start = segment["start"]
            end = segment["end"]
            words = segment["text"].split()

            # Add words to the current interval
            current_words.extend(words)

            # Check if we've passed the current interval
            while start >= current_time + interval:
                wpm = (len(current_words) / interval) * 60
                time_wpm.append((current_time, wpm))
                current_words = []  # Reset for the next interval
                current_time += interval

        # Process any remaining words
        if current_words:
            wpm = (len(current_words) / interval) * 60
            time_wpm.append((current_time, wpm))

        return time_wpm

    @staticmethod
    def plot_wpm(time_wpm, output_path="wpm_analysis.png"):
        """
        Plot the WPM over time.

        Args:
            time_wpm (list): A list of tuples (time, wpm) for each interval.
            output_path (str): Path to save the resulting plot.

        Returns:
            None
        """
        times, wpms = zip(*time_wpm) if time_wpm else ([], [])
        plt.figure(figsize=(10, 6))
        plt.plot(times, wpms, label="Words per Minute (WPM)", color='blue')
        plt.title("Speech Speed Analysis")
        plt.xlabel("Time (seconds)")
        plt.ylabel("WPM")
        plt.legend()
        plt.grid(True)
        plt.savefig(output_path)
        plt.show()
        print(f"WPM analysis plot saved to {output_path}")

    def get_general_info(self):
        """
        This method returns general information about the recorded audio file

        For the given audio file, this method returns information about language, length,
        topic, recording date and time, count of words, etc.


        Returns:
            tuple:
                - str: a machine generated title for the recording.
                - str: the language used in the recording.
                - ??: length of the recording in format min:sec
                - ??: Date and time when the audio was recorded.
                - int: count of words in the recording
        """
        pass