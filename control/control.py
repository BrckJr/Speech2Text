import time
from model.model import AudioModel
from view.view import AudioView


class AudioController:
    """
    The AudioController class acts as the intermediary between the Model (AudioModel)
    and the View (AudioView). It controls the flow of data and manages user interaction.

    Attributes:
        model (AudioModel): The model that handles audio recording and transcription.
        view (AudioView): The view that handles displaying information to the user.

    Methods:
        run(): Starts the audio recording and transcription process, managing the flow of the program.
        save_text_to_file(text): Saves the transcribed text to a file named 'output.txt'.
    """

    def __init__(self):
        """
        Initializes the AudioController by creating instances of the AudioModel and AudioView.
        """
        self.model = AudioModel()
        self.view = AudioView()

    def run(self):
        """
        The main control loop for the program. It continuously records audio, transcribes it,
        and displays the text. It also handles saving the transcriptions to a file.

        This loop will run until the user interrupts the program (e.g., using a keyboard interrupt).
        """
        while True:
            try:
                # Record and transcribe audio
                text = self.model.record_audio()
                if text:  # Check if text was successfully transcribed
                    self.view.display_text(text)  # Display the transcribed text
                    self.save_text_to_file(text)  # Save the text to a file
                time.sleep(1)  # Brief pause before the next recording
            except KeyboardInterrupt:
                self.view.show_exit_message()  # Show exit message when interrupted
                break

    def save_text_to_file(self, text):
        """
        Saves the transcribed text to a file called 'output.txt'.

        Args:
            text (str): The text to be written to the file.

        Returns:
            None: If the text is successfully written to the file, it does not return any value.

        Raises:
            Exception: If there is any error while writing to the file, it will display an error message.
        """
        try:
            with open("output.txt", "a") as file:
                file.write(text + "\n")  # Write the transcribed text followed by a newline
            print("Text written to output.txt")
        except Exception as e:
            self.view.display_error(f"Failed to save text: {e}")
