from sqlite3 import IntegrityError
from src.model.transcriber import Model
from src.model.analytics import Analytics
from src.database.models import AudioTranscription

from datetime import datetime

# Custom error classes
class TranscriptionStoringError(Exception): pass
class AudioStoringError(Exception): pass


def stop_recording_and_save_files(transcriber):
    """
    Stop the audio recording, save the audio file, and transcribe it.

    Args:
        transcriber (Transcriber): An instance of the transcriber class responsible for stopping the recording
                                   and transcribing the audio.

    Returns:
        tuple: A tuple containing the full paths for the audio file and the transcription file,
                as well as the transcription segments.

    Raises:
        AudioStoringError: If an error occurs during the storage of the audio file.
        TranscriptionStoringError: If an error occurs during the storage of the transcription file.
    """
    # Stop recording and save the audio file
    audio_filepath, audio_save_successful = transcriber.stop_recording_audio(True)

    if not audio_save_successful:
        raise AudioStoringError("Error occurred during storage of audio file")

    # Transcribe the recording and save the transcription file
    transcription_filepath, transcription_save_successful, segments, word_count, language = transcriber.transcribe_raw_audio(audio_filepath, True)

    if not transcription_save_successful:
        raise TranscriptionStoringError("Error occurred during storage of transcription file")

    return audio_filepath, transcription_filepath, segments, word_count, language

def transcribe_and_analyse(transcriber, current_user, db):
    """
    Transcribe audio, do analysis of the audio recording, and save the analysis to the database.

    Args:
        transcriber (Transcriber): An instance of the transcriber class to handle audio transcription.
        current_user (User): The current user requesting the transcription and analysis.
        db (Database): The database instance where information is stored.

    Returns:
        tuple: A tuple containing a dictionary with success status and message, the HTTP status code and the full
                audio filepath.
    """
    try:
        # Attempt to stop recording and save the files
        try:
            audio_filepath, transcription_filepath, segments, word_count, language = stop_recording_and_save_files(transcriber)
        except Exception as e:
            return {"success": False, "message": f"Failed to stop recording and save files due to error {e}."}, 500

        # Create a new analytics object to analyze the current audio
        analytics = Analytics(audio_filepath, transcription_filepath, segments, word_count, language)
        try:
            # Generate the speech speed graphic plot and get the filepath
            speech_speed_graphic_path = analytics.generate_plot_wpm()

            # Get the general info of the audio file
            title, language, audio_length, created_at, word_count = analytics.get_general_info()

            # Get the summary of the transcription
            summary = analytics.get_summary()
        except ValueError as value_error:
            return {"success": False, "message": f"Failed to generate analytics due to error {value_error}."}, 500

        # Save information to the database
        response, status_code = save_info_to_database(
            current_user=current_user,
            db=db,
            audio_filepath=audio_filepath,
            transcription_filepath=transcription_filepath,
            created_at= created_at,
            speech_speed_graphic_path=speech_speed_graphic_path,
            title=title,
            language=language,
            audio_length=audio_length,
            word_count= word_count,
            summary=summary
        )



        return response, status_code, audio_filepath

    except Exception as e:
        return {"success": False, "message": f"An internal error during transcription and analysis. Error message: {e}."}, 500

def save_info_to_database(current_user, db, audio_filepath, created_at, transcription_filepath,
                        speech_speed_graphic_path, title, language, audio_length, word_count, summary ):
    """
    Saves audio and transcription information to the database if the user is authenticated.

    Args:
        current_user (User): The currently logged-in user.
        db (SQLAlchemy): The database session object.
        audio_filepath (str): The full relative path to the saved audio file.
        created_at (datetime): Timestamp at which the audio file was created.
        transcription_filepath (str): The full relative path to the saved transcription file.
        speech_speed_graphic_path (str): The full relative path to the saved graphic from speed analysis.
        title (str): The AI generated title of the transcription.
        language (str): The language of the transcription.
        audio_length (float): Length of the audio file in seconds
        word_count (int): The number of words in the transcription.
        summary (str): The AI generated summary of the transcription.

    Returns:
        tuple: A response dictionary and an HTTP status code.
    """

    # Check if the current user is authenticated
    if current_user.is_authenticated:

        # Create a new AudioTranscription object with the given data
        audio_recording = AudioTranscription(
            user_id=current_user.id,  # Associate the recording with the user's ID
            audio_path=audio_filepath,  # Path to the audio file
            transcription_path=transcription_filepath,  # Path to the transcription file
            created_at = created_at, # Timestamp when the respective audio recording was created
            speech_speed_graphic_path = speech_speed_graphic_path,  # Link to the stored graphic from speed analysis
            title = title, # AI generated title for the transcription
            language = language, # Language of the audio and transcription
            audio_length = audio_length, # Length of the transcription in seconds
            word_count = word_count, # Number of words in the respective transcription
            summary = summary # AI generated summary of the transcription. Adapt size if necessary.
        )

        try:
            # Add the new record to the database session
            db.session.add(audio_recording)
            # Commit the changes to save the record in the database
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            return {"success": False, "message": "File paths must be unique."}, 400

        # Return a success response with the paths to the saved files
        return {
            "audio_path": audio_filepath,
            "transcription_path": transcription_filepath,
        }, 201  # HTTP 201 Created

    # If the user is not authenticated, return an error response
    return {"message": "User not authenticated"}, 401  # HTTP 401 Unauthorized

