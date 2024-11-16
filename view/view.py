import tkinter as tk
from tkinter import messagebox

class AudioView:
    """
    A GUI-based application for simulating audio recording functionality.

    This class provides a simple interface with buttons to start and stop the
    audio recording process. It is responsible for displaying the user interface
    elements in the Tkinter window.
    """

    def __init__(self, root):
        """
        Initializes the AudioView class.

        This method sets up the main Tkinter window, initializes the interface components,
        and arranges them using Tkinter's packing geometry.

        Args:
            root (tk.Tk): The root Tkinter window, passed from the controller.
        """
        self.root = root
        self.root.title("Transcriber Interface")
        self.root.geometry("400x300")
        self.is_recording = False

        # Create and pack header label
        self.header = tk.Label(root, text="Transcriber Interface", font=("Helvetica", 24, "bold"))
        self.header.pack(pady=20)

        # Create and pack the 'Start Recording' button
        self.start_button = tk.Button(root, text="Start Recording")
        self.start_button.pack(pady=10)

        # Create and pack the 'Stop Recording' button (disabled by default)
        self.stop_button = tk.Button(root, text="Stop Recording", state="disabled")
        self.stop_button.pack(pady=10)

    def show_transcription_prompt(self):
        """
        Displays a prompt asking the user whether they want to transcribe the saved recording.

        This method shows a message box with options to confirm (Yes) or cancel (No) transcription.

        Returns:
            bool: `True` if the user selects "Yes" to transcribe, `False` if "No" is selected.
        """

        self.root.withdraw()  # Hide the main tkinter window
        response = messagebox.askyesno(
            "Transcription Confirmation",
            "Recording has been saved. Would you like to transcribe it?"
        )
        self.root.deiconify() # Show the main tkinter window again
        return response
