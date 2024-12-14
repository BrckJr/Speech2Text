import os
from sqlite3 import IntegrityError
from src.model.analytics import Analytics
from src.database.models import AudioTranscription
import src.utils.utils as utils
from pydub import AudioSegment
from src.database import db

# Path to the stored raw audio files and transcriptions
AUDIO_FOLDER = "src/static/output/raw_audio/"
TRANSCRIPTION_FOLDER = "src/static/output/transcription/"

class UnauthorizedUserException(Exception):
    """
    Custom exception when unauthorized user tries to access database
    """
    pass

def store_audio(file):
    """
    Return a unique filename under which the audio file is stored.

    If the file object contains a name, extract it and check the database if the name is already used.
    If so, append a (1), (2), ... to the filename so it is unique.
    If no name is provided, generate a proprietary filename including the current timestamp with the utils file.

    Args:
        file (werkzeug.datastructures.FileStorage): audio file name inserted by the user

    Returns:
        str: path to the stored audio file

    Raises:
        IOError: If saving or processing the file fails.
    """

    # Generate filename or use default
    filename = file.filename or utils.get_default_audio_filename()

    # Base filename and extension
    base_name, extension = filename.rsplit('.', 1) if '.' in filename else (filename, '')

    # Ensure unique filename
    unique_filename = filename
    audio_filepath = os.path.join(AUDIO_FOLDER, f"{unique_filename}.wav")
    counter = 1
    try:
        while db.session.query(AudioTranscription).filter_by(audio_path=audio_filepath).first():
            unique_filename = f"{base_name}({counter}){'.' + extension if extension else ''}"
            audio_filepath = os.path.join(AUDIO_FOLDER, f"{unique_filename}.wav")
            counter += 1
    except Exception as e:
        raise IOError(f"Database query failed: {e}")

    # Save temporary file
    temp_filepath = os.path.join(AUDIO_FOLDER, f"temp_{unique_filename}.wav")
    try:
        file.save(temp_filepath)

        # Convert to .wav if needed
        if extension.lower() not in ['wav']:
            audio = AudioSegment.from_file(temp_filepath)
            audio.export(audio_filepath, format="wav")
            os.remove(temp_filepath)  # Remove the temporary file after conversion
        else:
            # Rename the temporary file to the final path
            os.rename(temp_filepath, audio_filepath)

        return audio_filepath

    except Exception as e:
        raise IOError(f"Invalid file: {e}")

    finally:
        # Ensure cleanup of the temporary file
        if os.path.exists(temp_filepath):
            os.remove(temp_filepath)

def transcribe_and_analyse(transcriber, current_user, audio_filepath):
    """
    Transcribe the audio file, perform analytics on the transcription, and save the results to the database.

    This function handles the process of transcribing an audio file, generating various analytics from the transcription,
    and storing the results in the database. It raises appropriate exceptions if any step fails during the process.

    Args:
        transcriber (Transcriber): An instance of the `Transcriber` class that is responsible for transcribing the audio file.
        current_user (User): The authenticated user who requested the transcription and analysis.
        audio_filepath (str): The path to the audio file that needs to be transcribed and analyzed.

    Returns:
        None

    Raises:
        RuntimeError: If transcription fails, analytics generation fails, or any unexpected error occurs during the process.
        ValueError: If the analytics generation fails (e.g., due to invalid or missing data).
        UnauthorizedUserException: If the user is not authenticated and attempts to access the database.

    """

    # Transcribe the audio file
    try:
        transcription_filepath, segments, word_count, language = transcriber.transcribe_raw_audio(audio_filepath)
    except Exception as e:
        raise RuntimeError(f"Failed to transcribe the audio file: {str(e)}")

    # Create a new analytics object and process the data
    analytics = Analytics(audio_filepath, transcription_filepath, segments, word_count, language)

    try:
        # Generate all analytics and gather the required data
        speech_speed_graphic_path = analytics.generate_plot_wpm()
        title, language, audio_length, created_at, word_count = analytics.get_general_info()
        summary = analytics.get_summary()
        pitch_graphic_path = analytics.analyze_pitch()
        energy_graphic_path = analytics.analyze_energy()
        improved_text_path = analytics.improve_text()
    except RuntimeError as e:
        raise RuntimeError(f"Failed to generate analytics: {str(e)}")
    except Exception as e:
        raise RuntimeError(f"Unexpected error during analytics generation: {str(e)}")

    # Create a dictionary of audio data
    audio_data = {
        "current_user": current_user,
        "audio_filepath": audio_filepath,
        "transcription_filepath": transcription_filepath,
        "created_at": created_at,
        "speech_speed_graphic_path": speech_speed_graphic_path,
        "pitch_graphic_path": pitch_graphic_path,
        "energy_graphic_path": energy_graphic_path,
        "improved_text_path": improved_text_path,
        "title": title,
        "language": language,
        "audio_length": audio_length,
        "word_count": word_count,
        "summary": summary,
    }

    # Save data to the database
    try:
        save_info_to_database(audio_data)
        return
    except IntegrityError as e:
        raise RuntimeError(f"Error: {str(e)}") # Error during data upload to database
    except UnauthorizedUserException:
        raise RuntimeError(f"Unauthorized user tried to access database.") # Error because of unauthorized access
    except Exception as e:
        raise RuntimeError(f"Failed to save audio data to the database: {str(e)}")

def save_info_to_database(audio_data):
    """
    Save audio transcription and analysis information to the database.

    This function creates a new `AudioTranscription` record in the database
    using the data provided in the `audio_data` dictionary. The user associated
    with the data must be authenticated. If the user is not authenticated or
    a database operation fails, appropriate exceptions are raised.

    Args:
        audio_data (dict): A dictionary containing the following keys:
            - current_user (User): The authenticated user who owns the recording.
            - audio_filepath (str): The path to the stored audio file.
            - transcription_filepath (str): The path to the transcription file.
            - created_at (datetime): The timestamp when the audio was created.
            - speech_speed_graphic_path (str): Path to the speech speed analysis graphic.
            - pitch_graphic_path (str): Path to the pitch analysis graphic.
            - energy_graphic_path (str): Path to the energy analysis graphic.
            - improved_text_path (str): Path to the improved text file.
            - title (str): AI-generated title for the transcription.
            - language (str): The language of the audio and transcription.
            - audio_length (float): The length of the audio in seconds.
            - word_count (int): The word count of the transcription.
            - summary (str): AI-generated summary of the transcription.

    Returns:
        None

    Raises:
        UnauthorizedUserException: If the user is not authenticated.
        IntegrityError: If a database operation fails (e.g., due to a duplicate entry).
    """

    # Check if the current user is authenticated
    current_user = audio_data.get("current_user")

    if not current_user.is_authenticated:
        raise UnauthorizedUserException() # If the user is not authenticated, raise an error

    # Create a new AudioTranscription object with the given data
    audio_recording = AudioTranscription(
        user_id=current_user.id,  # Associate the recording with the user's ID
        audio_path=audio_data["audio_filepath"],  # Path to the audio file
        transcription_path=audio_data["transcription_filepath"],  # Path to the transcription file
        created_at=audio_data["created_at"],  # Timestamp when the respective audio recording was created
        speech_speed_graphic_path=audio_data["speech_speed_graphic_path"],  # Link to the stored graphic from speed analysis
        pitch_graphic_path=audio_data["pitch_graphic_path"],  # Link to the stored graphic from pitch analysis
        energy_graphic_path=audio_data["energy_graphic_path"],  # Link to the stored graphic from energy analysis
        improved_text_path=audio_data["improved_text_path"],  # Link to the stored improved text
        title=audio_data["title"],  # AI-generated title for the transcription
        language=audio_data["language"],  # Language of the audio and transcription
        audio_length=audio_data["audio_length"],  # Length of the transcription in seconds
        word_count=audio_data["word_count"],  # Number of words in the respective transcription
        summary=audio_data["summary"]  # AI-generated summary of the transcription.
    )

    try:
        # Add the new record to the database session
        db.session.add(audio_recording)
        # Commit the changes to save the record in the database and return
        db.session.commit()
        return
    except IntegrityError:
        # If any exception happens during the update of the database, raise an error
        db.session.rollback()
        raise IntegrityError(f"Failed to update database.")

def cleanup(current_user, audio_filepath=None):
    """
    Delete audio files either for a specific file (if `audio_filepath` is provided) or for all files of a user.

    Args:
        current_user (User): The user requesting to delete the files.
        audio_filepath (str, optional): Path to a specific audio file to delete. If None, delete all files for the user.

    Raises:
        IntegrityError: If an error occurs during the database operation.
    """

    def cleanup_filesystem(files):
        """
        Deleting files in output directory.

        Cleans up the output directory by removing existing files,
        including all raw audio files, transcriptions, etc. for a specific user
        included in the files_to_delete list.

        Args:
            files (list of str): The list of audio files to delete for a specific user.
        """
        try:
            # Delete the files contained in the files_to_delete list
            for file in files:
                for attribute in [
                    'audio_path',
                    'transcription_path',
                    'speech_speed_graphic_path',
                    'improved_text_path',
                    'energy_graphic_path',
                    'pitch_graphic_path',
                    'improved_text_path'
                ]:
                    file_path = getattr(file, attribute, None)
                    if os.path.isfile(file_path):
                        os.remove(file_path)
        except Exception as cleanup_error:
            raise RuntimeError(f"Error during cleanup of files: {str(cleanup_error)}")

    try:
        # Conditionally filter based on the presence of audio_filepath
        if audio_filepath:
            # Query for a specific audio file for the current user
            files_to_delete = AudioTranscription.query.filter_by(audio_path=audio_filepath, user_id=current_user.id).all()
            # Delete the specific file(s)
            db.session.query(AudioTranscription).filter_by(audio_path=audio_filepath, user_id=current_user.id).delete()
        else:
            # Query for all files belonging to the current user
            files_to_delete = AudioTranscription.query.filter_by(user_id=current_user.id).all()
            # Delete all user files
            db.session.query(AudioTranscription).filter_by(user_id=current_user.id).delete()

        # Delete the files from the local filesystem
        cleanup_filesystem(files_to_delete)

        # Commit the database changes
        db.session.commit()

    except IntegrityError as e:
        # Handle any database integrity issues
        db.session.rollback()
        raise IntegrityError(f"Failed to update database: {str(e)}")

def get_user_files(current_user):
    """
    Fetches the file paths for audio recordings, transcriptions, and improved texts for the authenticated user.

    Args:
        current_user (User): The authenticated user.

    Returns:
        dict: A dictionary containing lists of audio file paths, transcription file paths,
              improved text file paths, and the corresponding creation timestamps.

    Raises:
        RuntimeError: If an error occurs during extraction of information from the database.
    """
    try:
        # Query the database for all audio recordings of the current user
        audio_recordings = AudioTranscription.query.filter_by(user_id=current_user.id).all()

        # Create a list of file paths and creation timestamps
        audio_files = [recording.audio_path for recording in audio_recordings]
        transcription_files = [recording.transcription_path for recording in audio_recordings]
        improved_text_files = [recording.improved_text_path for recording in audio_recordings]
        date_times = [recording.created_at for recording in audio_recordings]

        return {
            'audio_files': audio_files,
            'transcription_files': transcription_files,
            'improved_text_files': improved_text_files,
            'date_times': date_times
        }
    except Exception as e:
        raise RuntimeError(f"Error during loading of file lists: {str(e)}")

def get_analytics(audio_filepath):
    """
    Extract relevant analytics data from the AudioTranscription object.

    Args:
        audio_filepath (str): The path to the audio file for which analytics are requested.

    Returns:
        dict: A dictionary containing the extracted analytics data.

    Raises:
        RuntimeError: If an error occurs during extraction of information from the database.
    """
    try:
        target_database_entry = db.session.query(AudioTranscription).filter_by(audio_path=audio_filepath).first()
        return {
            'created_at': target_database_entry.created_at,
            'transcribed_text_path': target_database_entry.transcription_path,
            'speech_speed_graphic_path': target_database_entry.speech_speed_graphic_path,
            'pitch_graphic_path': target_database_entry.pitch_graphic_path,
            'energy_graphic_path': target_database_entry.energy_graphic_path,
            'improved_text_path': target_database_entry.improved_text_path,
            'recording_title': target_database_entry.title,
            'recording_language': target_database_entry.language,
            'audio_length': target_database_entry.audio_length,
            'word_count': target_database_entry.word_count,
            'text_summary': target_database_entry.summary
        }
    except Exception as e:
        raise RuntimeError(f"Error during loading of analytics information: {str(e)}")
