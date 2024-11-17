import tkinter as tk
from model.model import AudioModel
from view.view import AudioView
import threading

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
        self.view = AudioView()

        # Connect buttons to actions
        self.view.start_button.configure(command=self.start_recording)
        self.view.stop_button.configure(command=self.stop_recording)
        self.view.pause_button.configure(command=self.pause_recording)

    def run(self):
        """
        Starts the Tkinter main event loop.

        This method keeps the application running and responsive.
        """
        self.view.mainloop()

    def start_recording(self):
        """
        Handles the 'Start Recording' button action.

        This method calls the model to begin the recording process and updates
        the GUI to reflect the recording state by disabling the 'Start' button
        and enabling the 'Stop' button.
        """
        self.model.start_recording_audio()
        self.view.start_button.configure(state="disabled")
        self.view.stop_button.configure(state="normal")
        self.view.pause_button.configure(state="normal")

        # Update button colors
        self.view.start_button.configure(fg_color="lightgrey")  # Start button in dark grey
        self.view.stop_button.configure(fg_color="red")  # Stop button in red
        self.view.pause_button.configure(fg_color="darkgrey")  # Pause button in dark grey


        print("Recording started.")

    def pause_recording(self):
        """
         Handles the 'Pause Recording' button action.

         This method calls the model to pause the recording process and updates
         the GUI to reflect the recording state by enabling the 'Start' button
         and enabling the 'Stop' button.
         """
        continue_symbol = "\u23F5"  # Pause symbol

        self.model.pause_recording_audio()
        self.view.start_button.configure(state="normal")
        self.view.stop_button.configure(state="normal")
        self.view.pause_button.configure(state="disabled")

        # Update button colors and symbols
        self.view.start_button.configure(text=f"Continue\n{continue_symbol}")
        self.view.start_button.configure(fg_color="green")  # Continue button in light green
        self.view.stop_button.configure(fg_color="red")  # Stop button in red
        self.view.pause_button.configure(fg_color="lightgrey")  # Pause button in light grey

        print("Recording paused.")

    def stop_recording(self):
        """
        Handles the 'Stop Recording' button action.

        This method calls the model to stop the recording process and issues
        the view to prompt a window which allows the user to select if recorded
        audio should be transcribed or not.
        """
        start_symbol = "\u23FA" # Start symbol ("⏺︎"︎)

        filepath = self.model.stop_recording_audio()
        self.view.start_button.configure(state="normal")
        self.view.stop_button.configure(state="disabled")
        self.view.pause_button.configure(state="disabled")

        # Update button colors
        self.view.start_button.configure(text=f"Start\n{start_symbol}")
        self.view.start_button.configure(fg_color="green")  # Start button in green
        self.view.stop_button.configure(fg_color="lightgrey")  # Stop button in light grey
        self.view.pause_button.configure(fg_color="lightgrey")  # Pause button in light grey

        # Triggering prompt if user wants to transcribe audio input
        transcription_required = self.view.show_transcription_prompt()
        if transcription_required:
            print(f"Transcribing audio: {filepath}")

            # Create and start a thread for transcription to avoid blocking the UI unnecessarily long
            transcription_thread = threading.Thread(
                target=self.model.transcribe_raw_audio,
                args=(filepath,),
                daemon=True  # Set daemon=True if the thread should terminate with the program
            )
            transcription_thread.start()
        else:
            print("Recording discarded. No transcription will be done.")

