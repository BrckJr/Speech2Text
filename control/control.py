import tkinter as tk
from model.model import AudioModel
from view.view import AudioView
import threading
import subprocess

class AudioController:
    """
    The AudioController class coordinates interaction between the GUI (view) and the audio recording model.

    It manages user inputs via the view (such as starting, pausing, and stopping recordings) and
    handles communication with the AudioModel to control the recording process and trigger transcription.
    """

    def __init__(self):
        """
        Initializes the AudioController, setting up the model, the GUI window, and the view components.

        This method connects the start, stop, pause, and delete buttons to their corresponding actions
        in the controller.

        Attributes:
            model (AudioModel): The AudioModel instance to handle recording logic.
            root (tk.Tk): The root Tkinter window for the GUI.
            view (AudioView): The view instance managing the GUI elements.
        """

        self.model = AudioModel()
        self.root = tk.Tk()
        self.view = AudioView(self.root)

        # Connect buttons to actions
        self.view.start_button.config(command=self.start_recording)
        self.view.stop_button.config(command=self.stop_recording)
        self.view.pause_button.config(command=self.pause_recording)
        self.view.delete_all_files_button.config(command=self.delete_all_files)

    def run(self):
        """
        Starts the Tkinter main event loop.

        This method enters the Tkinter event loop, making the application responsive to user interactions
        through the GUI.
        """

        self.root.mainloop()

    def start_recording(self):
        """
        Handles the 'Start Recording' button action.

        This method triggers the start of the audio recording process in the model and updates
        the GUI to reflect the active recording state. The 'Start' button is disabled, while
        the 'Stop' and 'Pause' buttons are enabled.
        """

        self.model.start_recording_audio()
        self.view.start_button.config(state="disabled")
        self.view.stop_button.config(state="normal")
        self.view.pause_button.config(state="normal")

        print("Recording started.")

    def pause_recording(self):
        """
        Handles the 'Pause Recording' button action.

        This method pauses the audio recording process in the model and updates the GUI to reflect
        the paused state. The 'Start' button is re-enabled with a 'Continue' label, and the 'Pause'
        button is disabled.
        """

        continue_symbol = "\u23F5"  # Pause symbol

        self.model.pause_recording_audio()
        self.view.start_button.config(state="normal")
        self.view.stop_button.config(state="normal")
        self.view.pause_button.config(state="disabled")

        self.view.start_button.config(text=f"Continue\n{continue_symbol}")

        print("Recording paused.")

    def stop_recording(self):
        """
        Handles the 'Stop Recording' button action.

        This method stops the audio recording process and updates the GUI to reflect the stopped state.
        It triggers a prompt asking the user whether the recorded audio should be transcribed or discarded.
        """

        start_symbol = "\u23FA" # Start symbol ("⏺︎"︎)

        filepath, save_successful = self.model.stop_recording_audio()
        self.view.start_button.config(state="normal")
        self.view.stop_button.config(state="disabled")
        self.view.pause_button.config(state="disabled")

        self.view.start_button.config(text=f"Start\n{start_symbol}")

        # If save was not successful, return restart without transcribing
        if not save_successful:
            self.view.show_recording_error_prompt() # Show error prompt
            return

        # Update the listbox containing the raw audio files after saving was successful
        self.view.update_listbox("raw_audio")

        # Triggering saving prompt if user wants to transcribe audio input
        transcription_required = self.view.show_transcription_prompt()
        if transcription_required:
            print(f"Transcribing audio: {filepath}")

            # Create and start a thread for transcription to avoid blocking the UI unnecessarily long
            transcription_thread = threading.Thread(
                target=self.transcribe_and_update,
                args=(filepath,),
                daemon=True  # Set daemon=True if the thread should terminate with the program
            )
            transcription_thread.start()

        else:
            print("Recording discarded. No transcription will be done.")

    def transcribe_and_update(self, filepath):
        """
        Transcribes the audio file and updates the listbox once transcription is complete.

        This method runs in a separate thread to avoid blocking the UI during transcription. After the
        transcription is finished, it updates the view to reflect the new transcription.

        Args:
            filepath (str): The path to the audio file that should be transcribed.
        """

        self.model.transcribe_raw_audio(filepath)
        self.view.update_listbox("transcription")

    def delete_all_files(self):
        """
        Clears all files from the "raw_audio" and "transcription" subdirectories in the output directory.

        This method triggers a deletion prompt, and if confirmed, runs a shell script to clear the files
        and updates the listboxes to reflect the deleted files.
        """

        # Triggering deletion prompt and ask if user really wants to delete all files
        transcription_required = self.view.show_deletion_prompt()
        if transcription_required:
            script_path = "clear_output.sh"
            subprocess.run(["bash", script_path])

            # Update the list boxes after deletion
            self.view.update_listbox("transcription")
            self.view.update_listbox("raw_audio")
        else:
            print("Deletion of all files aborted.")



