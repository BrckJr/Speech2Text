import os
from datetime import datetime

def generate_output_directory(directory_path):
    """
    Generates output directory for given directory path.
    """

    os.makedirs(directory_path, exist_ok=True)

def generate_file_path(dir_name, filename=None):
    """
    Returns a relative path and name under which a file shall be stored including the time stamp.

    Args:
        dir_name (str): The type of file to store, e.g. "raw_audio", "transcription" or "speed_graphics".
        filename (str): Name which shall be used to generate new filename.
                        For 'transcription' and 'speed_graphics' this is only part of the name
                        to relate these files to the underlying audio recording.

    Returns:
        str: A relative storage path depending on the type of file ("src/static/output/...").
    """

    timestamp = datetime.now().strftime("%Y-%m-%dT%H-%M-%S")
    valid_filetypes = {
        "raw_audio": f"{filename}.wav",
        "transcription": f"transcription_of_{filename}.txt",
        "speed_graphics": f"speed_graphics_of_{filename}.png",
        "pitch_graphics": f"pitch_graphics_of_{filename}.png",
        "energy_graphics": f"energy_graphics_of_{filename}.png",
        "improved_text": f"improved_text_of_{filename}.txt",
    }

    filename = valid_filetypes.get(dir_name, f"corrupted_{timestamp}.txt")
    directory_path = f"src/static/output/{dir_name if dir_name in valid_filetypes else 'corrupted'}"

    generate_output_directory(directory_path)

    if dir_name not in valid_filetypes:
        raise ValueError("Unknown filetype called.")

    return os.path.join(directory_path, filename)

def get_default_audio_filename():
    """
    Returns a default filename for audio file including current timestamp.

    Returns:
        str: default audio filename.
    """

    timestamp = datetime.now().strftime("%Y-%m-%dT%H-%M-%S")
    return f"audio_recording_{timestamp}"