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
    # Save to the database if user is authenticated
    if current_user.is_authenticated:
        audio_recording = AudioTranscription(
            audio_path=stripped_audio_path,
            transcription_path=stripped_transcription_path,
            user_id=current_user.id
        )
        db.session.add(audio_recording)
        db.session.commit()

        return {
            "audio_path": stripped_audio_path,
            "transcription_path": stripped_transcription_path,
        }, 201

    return {"message": "User not authenticated"}, 401
