from sqlite3 import IntegrityError

from backend.model.transcriber import Model
from backend.database.models import AudioTranscription

def transcribe(transcriber, current_user, db):
    """
    Stops the recording, transcribes the audio, and saves it to the database.

    Args:
        transcriber (Model): The transcriber object responsible for handling the recording and transcription.
        current_user (User): The current authenticated user.
        db (SQLAlchemy): The database session.

    Returns:
        tuple: A tuple containing a response (Flask Response object) and HTTP status code.
    """
    try:
        # Stop recording and save the audio file
        audio_filepath, audio_save_successful = transcriber.stop_recording_audio(True)

        if not audio_save_successful:
            return {"success": False, "message": "Failed to save audio."}, 500

        stripped_audio_path = audio_filepath.replace('backend/static/', '')

        # Transcribe the recording
        transcription_filepath, transcription_save_successful, _ = transcriber.transcribe_raw_audio(audio_filepath,
                                                                                                    False)

        stripped_transcription_path = (
            transcription_filepath.replace('backend/static/', '') if transcription_save_successful else None
        )

        # Call method save_info_to_database to save the gained info to the database. None for not available info
        response, status_code = save_info_to_database(current_user, db, stripped_audio_path, stripped_transcription_path)
        return response, status_code

    except Exception as e:
        return {"success": False, "message": "An internal error occurred."}, 500

def transcribe_and_analyse(transcriber, current_user, db):
    """
    Stops the recording, transcribes the audio, analyzes it and saves everything to the database.

    Args:
        transcriber (Model): The transcriber object responsible for handling the recording and transcription.
        current_user (User): The current authenticated user.
        db (SQLAlchemy): The database session.

    Returns:
        tuple: A tuple containing a response (Flask Response object) and HTTP status code.
    """

    try:
        # Stop recording and save the audio file
        audio_filepath, audio_save_successful = transcriber.stop_recording_audio(True)

        if not audio_save_successful:
            return {"success": False, "message": "Failed to save audio."}, 500

        stripped_audio_path = audio_filepath.replace('backend/static/', '')

        # Transcribe the recording
        transcription_filepath, transcription_save_successful, segments = transcriber.transcribe_raw_audio(audio_filepath,
                                                                                                    True)

        stripped_transcription_path = (
            transcription_filepath.replace('backend/static/', '') if transcription_save_successful else None
        )

        # Call method save_info_to_database to save the gained info to the database. None for not available info
        response, status_code = save_info_to_database(current_user, db, stripped_audio_path, stripped_transcription_path)
        return response, status_code

    except Exception as e:
        return {"success": False, "message": "An internal error occurred."}, 500


def save_info_to_database(current_user, db, stripped_audio_path, stripped_transcription_path):
    """
    Saves audio and transcription information to the database if the user is authenticated.

    Args:
        current_user (User): The currently logged-in user.
        db (SQLAlchemy): The database session object.
        stripped_audio_path (str): The relative path to the saved audio file.
        stripped_transcription_path (str): The relative path to the saved transcription file.

    Returns:
        tuple: A response dictionary and an HTTP status code.
    """
    # Check if the current user is authenticated
    if current_user.is_authenticated:
        # Create a new AudioTranscription object with the given data
        audio_recording = AudioTranscription(
            audio_path=stripped_audio_path,  # Path to the audio file
            transcription_path=stripped_transcription_path,  # Path to the transcription file
            user_id=current_user.id  # Associate the recording with the user's ID
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
            "audio_path": stripped_audio_path,
            "transcription_path": stripped_transcription_path,
        }, 201  # HTTP 201 Created

    # If the user is not authenticated, return an error response
    return {"message": "User not authenticated"}, 401  # HTTP 401 Unauthorized

