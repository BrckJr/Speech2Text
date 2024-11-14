class AudioView:
    """
    The AudioView class handles displaying the transcribed text, error messages,
    and any exit messages to the user.

    Methods:
        display_text(text): Displays the transcribed text to the user.
        display_error(message): Displays an error message to the user.
        show_exit_message(): Displays a message when the program is exiting.
    """


    def display_text(self, text):
        """
        Displays the transcribed text to the user.

        Args:
            text (str): The transcribed text that was returned by the model.
        """
        print("Transcribed text:", text)

    def display_error(self, message):
        """
        Displays an error message to the user.

        Args:
            message (str): The error message to display.
        """
        print(f"Error: {message}")

    def show_exit_message(self):
        """
        Displays a message to the user when the program is exiting.
        """
        print("Program interrupted. Exiting...")