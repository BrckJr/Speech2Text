import os
from sqlite3 import IntegrityError
from src.model.analytics import Analytics
from src.database.models import AudioTranscription

class CleanupError(Exception):
    """Custom exception for cleanup errors."""
    pass

class TranscriptionStoringError(Exception):
    """Custom exception for transcription storing errors."""
    pass

def transcribe(transcriber, audio_filepath):
    """
    Trigger transcription the given audio file and save the transcription.

    Args:
        transcriber (Transcriber): An instance of the transcriber class responsible for handling audio transcription.
        audio_filepath (str): The path to the audio file to be transcribed.

    Returns:
        tuple: A tuple containing:
            - transcription_filepath (str): Path to the saved transcription file.
            - segments (list): List of transcription segments.
            - word_count (int): Total word count of the transcription.
            - language (str): Detected language of the transcription.

    Raises:
        TranscriptionStoringError: If an error occurs during the storage of the transcription file.
    """

    # Transcribe the recording and save the transcription file
    transcription_filepath, transcription_save_successful, segments, word_count, language = (
        transcriber.transcribe_raw_audio(audio_filepath)
    )

    # Raise an error if the transcription file could not be saved
    if not transcription_save_successful:
        raise TranscriptionStoringError("Error occurred during storage of transcription file")

    return transcription_filepath, segments, word_count, language

def transcribe_and_analyse(transcriber, current_user, db, audio_filepath):
    """
    Trigger transcription of audio, analysis of the recording, and saving of analysis results to the database.

    Args:
        transcriber (Transcriber): An instance of the transcriber class to handle audio transcription.
        current_user (User): The user requesting transcription and analysis.
        db (Database): The database instance to store analysis results.
        audio_filepath (str): The path to the audio file to be analyzed.

    Returns:
        tuple: A tuple containing:
            - response (dict): Dictionary with success status and message.
            - status_code (int): HTTP status code indicating success or failure.
    """
    try:
        # Attempt to stop recording and save the files
        try:
            transcription_filepath, segments, word_count, language = transcribe(transcriber, audio_filepath)
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

            # Get information about the pitch of the recording
            mean_pitch, std_pitch, pitch_range, pitch_graphic_path = analytics.analyze_pitch()

            # Get information about the energy level over time of the recording
            average_energy, std_energy, energy_graphic_path = analytics.analyze_energy()

            # Get filepath of the improved text
            improved_text_path, save_successful = analytics.improve_text()
        except ValueError as value_error:
            return {"success": False, "message": f"Failed to generate analytics due to error {value_error}."}, 500


        # Create a dictionary of audio data to pass
        audio_data = {
            "current_user": current_user,
            "db": db,
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

        # Save information to the database
        response, status_code = save_info_to_database(audio_data)

        return response, status_code

    except Exception as e:
        return {"success": False, "message": f"An internal error during transcription and analysis. Error message: {e}."}, 500

def save_info_to_database(audio_data):
    """
    Saves audio and transcription information to the database if the user is authenticated.

    Args:
        audio_data (dict): Dictionary containing audio, transcription and analysis information.

    Returns:
        tuple: A response dictionary and an HTTP status code.
    """
    # Check if the current user is authenticated
    current_user = audio_data.get("current_user")
    db = audio_data.get("db")

    if current_user.is_authenticated:
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
            # Commit the changes to save the record in the database
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            return {"success": False, "message": "File paths must be unique."}, 400

        # Return a success response with the paths to the saved files
        return {
            "audio_path": audio_data["audio_filepath"],
            "transcription_path": audio_data["transcription_filepath"],
        }, 201  # HTTP 201 Created

    # If the user is not authenticated, return an error response
    return {"message": "User not authenticated"}, 401  # HTTP 401 Unauthorized

def delete_files(files_to_delete):
    """
    Deleting files in output directory.

    Cleans up the output directory by removing existing files,
    including all raw audio files, transcriptions, etc. for a specific user
    included in the files_to_delete list.

    Args:
        files_to_delete (list of str): The list of audio files to delete for a specific user.
    """
    try:
        # Delete the files contained in the files_to_delete list
        for file in files_to_delete:
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
    except Exception:
        raise CleanupError("Error during cleanup")
