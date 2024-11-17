import os
from datetime import datetime


def generate_file_path(filetype):
    """
    Returns the relative path where the respective file shall be stored.

    Args:
        filetype (str): The type of file to store, either "raw_audio" or "transcription".

    Returns:
        _ (str): The relative storage path of the file.
    """

    timestamp = datetime.now().strftime("%Y-%m-%dT%H-%M-%S")
    valid_filetypes = {
        "raw_audio": f"raw_audio_{timestamp}.wav",
        "transcription": f"transcription_{timestamp}.txt",
    }

    filename = valid_filetypes.get(filetype, f"corrupted_{timestamp}.txt")
    directory_path = f"output/{filetype if filetype in valid_filetypes else 'corrupted'}"

    os.makedirs(directory_path, exist_ok=True)

    if filetype not in valid_filetypes:
        raise ValueError("Unknown filetype called.")

    return os.path.join(directory_path, filename)
