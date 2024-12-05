from sqlite3 import IntegrityError
from backend.model.transcriber import Model
from backend.model.analytics import Analytics
from backend.database.models import AudioTranscription

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
        tuple: A tuple containing the stripped paths for the audio file and the transcription file, as well as the transcription segments.

    Raises:
        AudioStoringError: If an error occurs during the storage of the audio file.
        TranscriptionStoringError: If an error occurs during the storage of the transcription file.
    """
    # Stop recording and save the audio file
    audio_filepath, audio_save_successful = transcriber.stop_recording_audio(True)

    if not audio_save_successful:
        raise AudioStoringError("Error occurred during storage of audio file")

    # Transcribe the recording and save the transcription file
    transcription_filepath, transcription_save_successful, segments = transcriber.transcribe_raw_audio(audio_filepath, True)

    if not transcription_save_successful:
        raise TranscriptionStoringError("Error occurred during storage of transcription file")

    # Strip the file paths for storage in the database
    stripped_audio_path = audio_filepath.replace('backend/static/', '')
    stripped_transcription_path = transcription_filepath.replace('backend/static/', '')

    return stripped_audio_path, stripped_transcription_path, segments

def transcribe_and_analyse(transcriber, current_user, db):
    """
    Transcribe audio, do analysis of the audio recording, and save the analysis to the database.

    Args:
        transcriber (Transcriber): An instance of the transcriber class to handle audio transcription.
        current_user (User): The current user requesting the transcription and analysis.
        db (Database): The database instance where information is stored.

    Returns:
        tuple: A tuple containing a dictionary with success status and message, and the HTTP status code.
    """
    try:
        # Attempt to stop recording and save the files
        try:
            stripped_audio_filepath, stripped_transcription_filepath, segments = stop_recording_and_save_files(transcriber)
        except Exception as e:
            return {"success": False, "message": f"Failed to save files due to error {e}"}, 500

        # Create a new analytics object to analyze the current audio
        analytics = Analytics(stripped_audio_filepath, stripped_transcription_filepath, segments)

        try:
            # Generate the speech speed graphic plot
            speech_speed_graphic_path = analytics.generate_plot_wpm()
        except ValueError:
            return {"success": False, "message": "An internal error occurred."}, 500

        # Save information to the database
        response, status_code = save_info_to_database(
            current_user=current_user,
            db=db,
            stripped_audio_path=stripped_audio_filepath,
            stripped_transcription_path=stripped_transcription_filepath,
            already_analysed=True,
            speech_speed_graphic_path=speech_speed_graphic_path
        )

        return response, status_code, stripped_audio_filepath

    except Exception as e:
        return {"success": False, "message": "An internal error occurred."}, 500

def save_info_to_database(current_user, db, stripped_audio_path, stripped_transcription_path, already_analysed=False,
                          speech_speed_graphic_path=None):
    """
    Saves audio and transcription information to the database if the user is authenticated.

    Args:
        current_user (User): The currently logged-in user.
        db (SQLAlchemy): The database session object.
        stripped_audio_path (str): The relative path to the saved audio file.
        stripped_transcription_path (str): The relative path to the saved transcription file.
        already_analysed (bool): Set to true parameters include the analysis info, default is false.
        speech_speed_graphic_path (str): The relative path to the saved graphic from speed analysis.

    Returns:
        tuple: A response dictionary and an HTTP status code.
    """
    # Check if the current user is authenticated
    if current_user.is_authenticated:
        # Create a new AudioTranscription object with the given data
        audio_recording = AudioTranscription(
            user_id=current_user.id,  # Associate the recording with the user's ID
            audio_path=stripped_audio_path,  # Path to the audio file
            transcription_path=stripped_transcription_path,  # Path to the transcription file
            already_analysed=already_analysed, # Change status in the database if transcription was analyzed
            speech_speed_graphic_path=speech_speed_graphic_path # Link to the stored graphic from speed analysis
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

