import tkinter as tk
from tkinter import messagebox
import customtkinter
from PIL import Image, ImageTk

class AudioView(customtkinter.CTk):
    """
    A GUI-based application for simulating audio recording functionality.

    This class provides a simple interface with buttons to start and stop the
    audio recording process. It is responsible for displaying the user interface
    elements in the Tkinter window.
    """

    def __init__(self):
        super().__init__()

        # Configure the window
        self.title("Transcriber Interface")

        # Get the screen width and height to make the window full screen
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        self.geometry(f"{screen_width}x{screen_height}")

        # Load the background image
        self.bg_image = tk.PhotoImage(
            file="view/figures/realistic-polygonal-background/realistic-polygonal-background.png")

        # Create a canvas to display the background (using grid instead of pack)
        self.canvas = tk.Canvas(self, width=screen_width, height=screen_height)
        self.canvas.grid(row=0, column=0, columnspan=4, rowspan=4, sticky="nsew")

        # Display the image on the canvas
        self.canvas.create_image(0, 0, image=self.bg_image, anchor="nw")
        # Create left sidebar frame with widgets
        self.sidebar_frame_left = customtkinter.CTkFrame(self, width=40, corner_radius=10)
        self.sidebar_frame_left.grid(row=0, column=0, rowspan=3, padx=(20, 20), pady=(20, 20), sticky="nsew")

        # Add the header label for the left sidebar
        self.header_left_sidebar = customtkinter.CTkLabel(self.sidebar_frame_left, text="Recorded Audio Files",
                                                          font=customtkinter.CTkFont(size=20, weight="bold"))
        self.header_left_sidebar.grid(row=0, column=0, padx=20, pady=(20, 10))

        # Create appearance mode selection in the left corner
        self.corner_frame_left = customtkinter.CTkFrame(self, width=40, corner_radius=10)
        self.corner_frame_left.grid(row=3, column=0, sticky="nsew", padx=(20, 20), pady=(20, 20))

        # Add the appearance mode label to the corner frame
        self.header_left_corner = customtkinter.CTkLabel(self.corner_frame_left, text="Appearance Mode",
                                                         font=customtkinter.CTkFont(size=20, weight="bold"))
        self.header_left_corner.grid(row=0, column=0, padx=20, pady=(20, 10))

        # Create model selection in the right corner
        self.corner_frame_right = customtkinter.CTkFrame(self, width=40, corner_radius=10)
        self.corner_frame_right.grid(row=3, column=3, sticky="nsew", padx=(20, 20), pady=(20, 20))

        # Add the model selection label to the right corner frame
        self.header_right_corner = customtkinter.CTkLabel(self.corner_frame_right, text="Mode Selection",
                                                          font=customtkinter.CTkFont(size=20, weight="bold"))
        self.header_right_corner.grid(row=0, column=0, padx=20, pady=(20, 10))

        # Create the right sidebar frame with widgets
        self.sidebar_frame_right = customtkinter.CTkFrame(self, width=40, corner_radius=10)
        self.sidebar_frame_right.grid(row=0, column=3, rowspan=3, padx=(20, 20), pady=(20, 20), sticky="nsew")

        # Add the header label for the right sidebar
        self.header_right_sidebar = customtkinter.CTkLabel(self.sidebar_frame_right, text="Transcription Files",
                                                           font=customtkinter.CTkFont(size=20, weight="bold"))
        self.header_right_sidebar.grid(row=0, column=0, padx=20, pady=(20, 10))

        # Create textbox with main header (bold and centered)
        self.header_main = customtkinter.CTkTextbox(self, font=("Roboto", 20, "bold"))
        self.header_main.grid(row=0, column=1, columnspan=2, sticky="nsew")
        self.header_main.insert("0.0", "Transcriber Interface")
        self.header_main.tag_add("center", "1.0", "end")
        self.header_main.configure(state="disabled")  # Make it non-editable

        # Create textbox with instructions
        self.instruction_label = customtkinter.CTkTextbox(self)
        self.instruction_label.grid(row=1, column=1, columnspan=2, sticky="nsew")
        self.instruction_label.insert("0.0", "Press the start button to begin recording. \n"
                                             "Press the pause button to pause the recording.\n"
                                             "Finish the recording by pressing the stop button.")

        # Create textbox with footer
        self.footer_label = customtkinter.CTkTextbox(self)
        self.footer_label.grid(row=3, column=1, columnspan=2, sticky="nsew")
        self.footer_label.insert("0.0", "Developed by Kilian Brickl © 2024")

        # Use symbols for the buttons
        start_symbol = "\u23FA"  # Start symbol ("⏺︎"︎)
        continue_symbol = "\u23F5"  # Continue symbol ("⏵︎︎)
        stop_symbol = "\u23F9"  # Stop symbol ("⏹︎"︎)
        pause_symbol = "\u23F8"  # Pause symbol ("⏸"︎)

        self.button_frame = customtkinter.CTkFrame(self)
        self.button_frame.grid(row=2, column=1, columnspan=2, sticky="nsew")
        self.button_frame.grid_rowconfigure(0, weight=1) # vertical centering
        self.button_frame.grid_columnconfigure((0, 1, 2), weight=1) # horizontal centering

        # Create the 'Start Recording' button
        self.start_button = customtkinter.CTkButton(
            self.button_frame,
            text=f"Start\n{start_symbol}",
            font=("Roboto", 20),
            fg_color="green",
            width=150,
            height=50
        )
        self.start_button.grid(row=0, column=0, padx=(10, 10), pady=(20, 20))

        # Create the 'Pause Recording' button
        self.pause_button = customtkinter.CTkButton(
            self.button_frame,
            text=f"Pause\n{pause_symbol}",
            font=("Roboto", 20),
            state="disabled",
            fg_color="lightgrey",
            width=150,
            height=50
        )
        self.pause_button.grid(row=0, column=1, padx=(10, 10), pady=(20, 20))

        # Create the 'Stop Recording' button
        self.stop_button = customtkinter.CTkButton(
            self.button_frame,
            text=f"Stop\n{stop_symbol}",
            font=("Roboto", 20),
            fg_color="lightgrey",
            state="disabled",
            width=150,
            height=50
        )
        self.stop_button.grid(row=0, column=2, padx=(10, 10), pady=(20, 20))

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