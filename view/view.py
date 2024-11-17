import tkinter as tk
from tkinter import messagebox
import customtkinter

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
        # Get the screen width and height to make the window full screen
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        self.root.geometry(f"{screen_width}x{screen_height}")

        # Set the minimum size of the window
        # self.root.minsize(400, 400)  # Minimum width and height
        # self.root.resizable(True, True)  # Allow resizing horizontally and vertically

        # Load the background image
        self.bg_image = tk.PhotoImage(file="view/figures/realistic-polygonal-background/realistic-polygonal-background.png", master=self.root)
        img_label = tk.Label(self.root, image=self.bg_image)
        img_label.place(x=0, y=0, relwidth=1, relheight=1)

        # Create and pack header label
        self.header = tk.Label(root, text="Transcriber Interface", font=("Helvetica", 24, "bold"), bg="white", fg="black")
        self.header.pack(pady=20)

        # Create a label with instructions or any other text
        self.instruction_label = tk.Label(self.root, text="Press the start button to begin recording. "
                                                          "\n Press the pause button to pause the recording"
                                                          "\n Finish the recording by pressing the stop button.", font=("Helvetica", 12), bg="white", fg="black")
        self.instruction_label.pack(pady=20)

        # Optional: Create a footer or other information label
        self.footer_label = tk.Label(self.root, text="Developed by Kilian Brickl © 2024", font=("Helvetica", 10, "italic"), bg="white", fg="black")
        self.footer_label.pack(side="bottom", pady=20)

        # Use symbols for the buttons
        start_symbol = "\u25B6"  # Unicode for play symbol (▶)
        stop_symbol = "\u23F9"  # Unicode for stop symbol (⏹)
        pause_symbol = "\u23F8" # Unicode for pause symbol (⏸︎)

        # Create and pack the 'Start Recording' button
        self.start_button = tk.Button(root, text=start_symbol, font=("Helvetica", 24, "bold"), fg="red", width=15, height=2, bd=0, highlightthickness=0)
        self.start_button.pack(pady=10)

        # Create and pack the 'Pause Recording' button
        self.pause_button = tk.Button(root, text=pause_symbol, state="disabled", font=("Helvetica", 24, "bold"), width=15, height=2, bd=0, highlightthickness=0)
        self.pause_button.pack(pady=10)

        # Create and pack the 'Stop Recording' button (disabled by default)
        self.stop_button = tk.Button(root, text=stop_symbol, state="disabled", font=("Helvetica", 24, "bold"), fg="red", width=15, height=2, bd=0, highlightthickness=0)
        self.stop_button.pack(pady=10)

        self.is_recording = False


    @staticmethod
    def show_transcription_prompt():
        """
        Displays a prompt asking the user whether they want to transcribe the saved recording.

        This method shows a message box with options to confirm (Yes) or cancel (No) transcription.

        Returns:
            bool: `True` if the user selects "Yes" to transcribe, `False` if "No" is selected.
        """

        response = messagebox.askyesno(
            "Transcription Confirmation",
            "Recording has been saved. Would you like to transcribe it?"
        )
        return response