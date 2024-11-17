from control.control import AudioController
from view.view import AudioView

if __name__ == "__main__":
    """
    The entry point of the program. This file starts the AudioController, which begins 
    the process of recording audio, transcribing it, and storing the results.
    """

    controller = AudioController()  # Create an instance of the controller
    controller.run()  # Start the control loop that manages the audio recording and transcription