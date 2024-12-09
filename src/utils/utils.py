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
        _ (str): A relative storage path depending on the type of file ("src/static/output/...").
    """

    timestamp = datetime.now().strftime("%Y-%m-%dT%H-%M-%S")
    valid_filetypes = {
        "raw_audio": f"audio_recording_{timestamp}.wav",
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

def get_sorted_files(dir_path):
    """
    Retrieves and sorts files in a directory by their timestamps embedded in filenames.

    Args:
        dir_path (str): Path to the directory containing the files.

    Returns:
        list: A list of filenames sorted in chronological order based on their timestamps.
    """
    files = [file for file in os.listdir(dir_path) if file.endswith((".txt", ".wav"))]

    # Sort files based on their extracted timestamps
    sorted_files = sorted(
        files,
        key=lambda file: extract_timestamp_from_filename(file)
    )
    return sorted_files

def extract_timestamp_from_filename(filename):
    """
    Extracts the timestamp from a filename and converts it to a datetime object.

    Assumes the timestamp is at the end of the filename, before the extension,
    and is in the format "%Y-%m-%dT%H-%M-%S".

    Args:
        filename (str): The filename from which to extract the timestamp.

    Returns:
        datetime: The extracted timestamp as a datetime object.
    """
    base_name = os.path.splitext(filename)[0]  # Remove the file extension
    timestamp_str = base_name.split("_")[-1]   # Extract the timestamp part
    return datetime.strptime(timestamp_str, "%Y-%m-%dT%H-%M-%S")

def extract_filetype_from_filename(filename):
    """
    Extracts the timestamp from a filename and converts it to a datetime object.

    Assumes the timestamp is at the end of the filename, before the suffix,
    and is in the format "%Y-%m-%dT%H-%M-%S".

    Args:
        filename (str): The filename from which to extract the part before the last underscore.

    Returns:
        str: The extracted part of the filename before the last underscore.
    """
    base_name = os.path.splitext(filename)[0]  # Remove the file extension
    front_part = "_".join(base_name.split("_")[:-1])  # Extract the part before the last underscore
    return front_part
