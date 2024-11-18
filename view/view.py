import os
import platform
import subprocess
import tkinter as tk
from tkinter import messagebox
import utils.utils as utils

class AudioView:
    """
    A GUI-based application for simulating audio recording functionality.

    This class provides a simple interface with buttons to start and stop the
    audio recording process. It is responsible for displaying the user interface
    elements in the Tkinter window.
    """

    def __init__(self, root):
        """
        Initializes the AudioView class with a grid layout.
        """

        # Initialize all objects on the window
        self.stop_button = None
        self.pause_button = None
        self.start_button = None
        self.delete_all_files_button = None
        self.bg_image = None
        self.footer_label = None
        self.instruction_label = None
        self.header = None
        self.transcriptions_box_label = None
        self.transcriptions_listbox = None
        self.raw_audios_box_label = None
        self.raw_audios_listbox = None
        self.transcription_model_dropdown = None
        self.selected_transcription_model = None
        self.transcription_model_dropdown_label = None
        self.file_frame_model_dropdown = None
        self.file_frame_raw_audio = None
        self.file_frame_transcription = None

        self.root = root
        self.root.title("Transcriber Interface")
        # Get the screen width and height to make the window full screen
        screen_width, screen_height = self.root.winfo_screenwidth(), self.root.winfo_screenheight()
        self.root.geometry("1080x720")  # Set original size of window
        # self.root.geometry(f"{screen_width}x{screen_height}")  # Set original size of window
        # self.root.minsize(1000, 650)  # Minimum size when scaling, may need improvement ...
        self.root.resizable(True, True)  # Allow resizing horizontally and vertically

        # Configure grid layout
        self.root.grid_columnconfigure(0, weight=1)  # Left column scalable
        self.root.grid_columnconfigure(1, weight=0)  # Middle column not scalable
        self.root.grid_columnconfigure(2, weight=1)  # Right column scalable
        self.root.grid_rowconfigure(0, weight=1) # Top row scalable
        self.root.grid_rowconfigure(1, weight=1) # Middle row not scalable
        self.root.grid_rowconfigure(2, weight=1) # Bottom row not scalable

        # Create components
        self.create_background()
        self.create_labels()
        self.create_buttons()
        self.create_transcriptions_file_list()
        self.create_raw_audio_file_list()
        self.create_dropdown_menus()

    def create_background(self):
        # Load the background image
        self.bg_image = tk.PhotoImage(
            file="view/figures/realistic-polygonal-background/realistic-polygonal-background.png",
            master=self.root
        )
        img_label = tk.Label(
            self.root,
            image=self.bg_image
        )
        img_label.place(x=0, y=0, relwidth=1, relheight=1)

    def create_labels(self):
        """Create labels in the middle column."""
        self.header = tk.Label(
            self.root,
            text="Transcriber Interface",
            font=("Helvetica", 30, "bold"),
            bg="white",
            fg="black"
        )
        self.header.grid(row=0, column=1)

        self.instruction_label = tk.Label(
            self.root,
            text="Press the start button to begin recording. "
                 "\nPress the pause button to pause the recording."
                 "\nFinish the recording by pressing the stop button.",
            font=("Helvetica", 18, "italic"),
            bg="white",
            fg="black"
        )
        self.instruction_label.grid(row=1, column=1, pady=(50, 100), sticky="n")

        self.footer_label = tk.Label(
            self.root,
            text="Developed by Kilian Brickl © 2024",
            font=("Helvetica", 10, "italic"),
            bg="white",
            fg="black"
        )
        self.footer_label.grid(row=2, column=1, pady=(10, 20), sticky="s")

    def create_buttons(self):
        """Create buttons in the middle column, placed side-by-side in a single row with the same size."""
        # Unicode symbols for the buttons
        start_symbol = "\u25B6"  # Unicode for play symbol (▶)
        stop_symbol = "\u23F9"  # Unicode for stop symbol (⏹)
        pause_symbol = "\u23F8"  # Unicode for pause symbol (⏸︎)
        bin_symbol = "\U0001F5D1" # Unicode for bin symbol (🗑)

        # Create the 'Start Recording' button
        self.start_button = tk.Button(
            self.root,
            text=f"Start\n{start_symbol}",
            font=("Roboto", 20),
            fg="green",
            width=7,
            height=3,
            borderwidth=0
        )
        self.start_button.grid(row=1, column=1, sticky="w")

        # Create the 'Pause Recording' button
        self.pause_button = tk.Button(
            self.root,
            text=f"Pause\n{pause_symbol}",
            font=("Roboto", 20),
            fg="black",
            state="disabled",  # Initially disabled
            width=7,
            height=3,
            borderwidth=0
        )
        self.pause_button.grid(row=1, column=1)

        # Create the 'Stop Recording' button
        self.stop_button = tk.Button(
            self.root,
            text=f"Stop\n{stop_symbol}",
            font=("Roboto", 20),
            fg="red",
            state="disabled",  # Initially disabled
            width=7,
            height=3,
            borderwidth=0
        )
        self.stop_button.grid(row=1, column=1, sticky="e")

        # Create the 'Reload Files' button
        self.delete_all_files_button = tk.Button(
            self.root,
            text=f"Delete all Files \n{bin_symbol}",
            font=("Roboto", 20),
            width=30,
            height=3,
            borderwidth=0
        )
        self.delete_all_files_button.grid(row=2, column=1, padx=(10, 20), pady=10, sticky="n")

    # noinspection DuplicatedCode
    def create_dropdown_menus(self):
        self.file_frame_model_dropdown = tk.Frame(self.root, bg="white", bd=2, relief="solid")
        self.file_frame_model_dropdown.grid(row=2, column=2, padx=(10, 20), pady=10, sticky="nsew")

        self.transcription_model_dropdown_label = tk.Label(
            self.file_frame_model_dropdown,
            text="Model Settings",
            font=("Helvetica", 18, "bold"),
            bg="white",
            fg="black"
        )
        self.transcription_model_dropdown_label.pack(pady=10)

        # Create a list of options for the dropdown
        options = ["Whisper (OpenAI)"]

        # Create a Tkinter variable for the dropdown (StringVar)
        self.selected_transcription_model = tk.StringVar()
        self.selected_transcription_model.set(options[0])  # Default selected option

        # Create the OptionMenu widget
        self.transcription_model_dropdown = tk.OptionMenu(
            self.file_frame_model_dropdown,
            self.selected_transcription_model,
            *options,
        )
        self.transcription_model_dropdown.configure(bg="lightgrey")
        self.transcription_model_dropdown.pack(padx=10, pady=10, fill="both", expand=True)

    # noinspection DuplicatedCode
    def create_transcriptions_file_list(self):
        """Create a file list widget in the rightmost column."""
        self.file_frame_raw_audio = tk.Frame(self.root, bg="white", bd=2, relief="solid")
        self.file_frame_raw_audio.grid(row=0, column=2, rowspan=2, padx=(10, 20), pady=10, sticky="nsew")

        self.transcriptions_box_label = tk.Label(
            self.file_frame_raw_audio,
            text="Transcribed Files",
            font=("Helvetica", 18, "bold"),
            bg="white",
            fg="black"
        )
        self.transcriptions_box_label.pack(pady=10)

        self.transcriptions_listbox = tk.Listbox(
            self.file_frame_raw_audio,
            font=("Helvetica", 14),
            width=30,
            height=20,
            selectmode="single",
            bg="lightgrey",
            fg="black"
        )
        self.transcriptions_listbox.pack(padx=10, pady=10, fill="both", expand=True)

        listbox_label = "transcription"
        self.update_listbox(listbox_label)

        self.transcriptions_listbox.bind("<<ListboxSelect>>", self.open_selected_file)

    # noinspection DuplicatedCode
    def create_raw_audio_file_list(self):
        """Create a file list widget in the leftmost column."""
        self.file_frame_transcription = tk.Frame(self.root, bg="white", bd=2, relief="solid")
        self.file_frame_transcription.grid(row=0, column=0, rowspan=2, padx=(10, 20), pady=10, sticky="nsew")

        self.raw_audios_box_label = tk.Label(
            self.file_frame_transcription,
            text="Raw Audio Files",
            font=("Helvetica", 18, "bold"),
            bg="white",
            fg="black"
        )
        self.raw_audios_box_label.pack(pady=10)

        self.raw_audios_listbox = tk.Listbox(
            self.file_frame_transcription,
            font=("Helvetica", 14),
            width=30,
            height=20,
            selectmode="single",
            bg="lightgrey",
            fg="black"
        )
        self.raw_audios_listbox.pack(padx=10, pady=10, fill="both", expand=True)

        listbox_label = "raw_audio"
        self.update_listbox(listbox_label)

        self.raw_audios_listbox.bind("<<ListboxSelect>>", self.open_selected_file)


    def update_listbox(self, listbox_label):
        """
        Updates the appropriate listbox with files based on the provided label.

        This method updates either the 'raw_audio' or 'transcription' listbox with files
        from the corresponding directory. It first fetches the files using
        `get_files_in_directory()` method, clears the existing listbox entries, and
        populates it with the new files.

        Args:
            listbox_label (str): A string indicating which listbox to update.
                                  It can be either "raw_audio" or "transcription".
        """
        # Get the files for the respective directory
        if listbox_label == "raw_audio":
            dir_path = "output/raw_audio"
            listbox = self.raw_audios_listbox
        elif listbox_label == "transcription":
            dir_path = "output/transcription"
            listbox = self.transcriptions_listbox
        else:
            # If the label is not valid, return early
            return

        # Fetch files and update the listbox
        files = utils.get_sorted_files(dir_path)

        # Clear existing entries and insert new ones
        listbox.delete(0, tk.END)
        listbox.insert(tk.END, *files)  # Efficiently add all files at once

    @staticmethod
    def open_selected_file(event):
        """
        Opens the file selected in the Listbox using the system's default application.

        Args:
            event: The Tkinter event triggered by selecting an item in the Listbox.
        """
        # Get the widget that triggered the event
        widget = event.widget

        # Get the index of the selected item
        selected_index = widget.curselection()
        if selected_index:
            # Get the selected file name
            selected_file = widget.get(selected_index[0])
            file_type = utils.extract_filetype_from_filename(selected_file)
            file_path = os.path.join("output", file_type, selected_file)
            try:
                # Open the file based on the operating system
                if platform.system() == "Windows":
                    os.startfile(file_path)  # Windows-specific
                elif platform.system() == "Darwin":  # macOS
                    subprocess.run(["open", file_path], check=True)
                else:  # Linux and other systems
                    subprocess.run(["xdg-open", file_path], check=True)
                print(f"File opened: {file_path}")
            except Exception as e:
                # Handle file opening errors
                print(f"Error opening file {file_path}: {e}")

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

    @staticmethod
    def show_recording_error_prompt():
        """
        Displays a prompt showing an error when the recorded audio file is empty
        """
        messagebox.showerror(
            "Recording Error",
            "Recording failed or cannot be stored, please try again."
        )

    @staticmethod
    def show_deletion_prompt():
        """
        Displays a prompt asking the user whether they want to delete all files.

        This method shows a message box warning the user that all files
        from the raw audio recordings and transcriptions will be deleted,
        and prompts for confirmation.

        Returns:
            bool: `True` if the user selects "Yes" to confirm deletion,
                  `False` if "No" is selected.
        """

        response = messagebox.askyesno(
            "Delete all Files",
            "All files from the raw audio recordings as well as the transcriptions will be deleted. Do you want to proceed?"
        )
        return response