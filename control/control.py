import tkinter as tk
from model.model import AudioModel
from view.view import AudioView


class AudioController:
    """
    Controller class that coordinates the interaction between the model and view.

    The `AudioController` manages user interactions through the GUI and
    communicates with the `AudioModel` to handle recording logic.
    """

    def __init__(self):
        """
        Initializes the AudioController.

        This sets up the model, the root Tkinter window, the view, and connects
        the start and stop button actions.
        """
        self.model = AudioModel()
        self.root = tk.Tk()
        self.view = AudioView(self.root)

        # Connect buttons to actions
        self.view.start_button.config(command=self.start_recording)
        self.view.stop_button.config(command=self.stop_recording)

    def run(self):
        """
        Starts the Tkinter main event loop.

        This method keeps the application running and responsive.
        """
        self.root.mainloop()

    def start_recording(self):
        """
        Handles the 'Start Recording' button action.

        This method calls the model to begin the recording process and updates
        the GUI to reflect the recording state by disabling the 'Start' button
        and enabling the 'Stop' button.
        """
        self.model.start_recording_audio()
        self.view.start_button.config(state="disabled")
        self.view.stop_button.config(state="normal")
        print("Recording started.")

    def stop_recording(self):
        """
        Handles the 'Stop Recording' button action.

        This method calls the model to stop the recording process and issues
        the view to prompt a window which allows the user to select if recorded
        audio should be transcribed or not.
        """
        filepath = self.model.stop_recording_audio()
        self.view.start_button.config(state="normal")
        self.view.stop_button.config(state="disabled")

        # Triggering prompt if user wants to transcribe audio input
        transcription_required = self.view.show_transcription_prompt()
        if transcription_required:
            print(f"Transcribing audio: {filepath}")
            self.model.transcribe_raw_audio(filepath)
        else:
            print("Recording discarded. No transcription will be done.")
