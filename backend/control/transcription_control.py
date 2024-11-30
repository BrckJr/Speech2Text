from flask import Blueprint, jsonify, send_from_directory, request, render_template
from flask_login import login_required, current_user
from backend.model.transcriber import Model
from backend.database import db
from backend.database.models import AudioTranscription

# Create a Blueprint for transcription routes
transcription_bp = Blueprint('transcription', __name__)

# Create an instance of the model which executes the actual logic
transcriber = Model()

# Path to the stored raw audio files and transcriptions
AUDIO_FOLDER = "backend/static/output/raw_audio"
TRANSCRIPTION_FOLDER = "backend/static/output/transcription"

@transcription_bp.route('/dashboard')
@login_required
def dashboard():
    """
    Displays the user's dashboard with all their uploaded audio files.

    Retrieves the list of audio transcription records from the database
    for the authenticated user and renders them in the 'dashboard' template.
    """
    user_files = AudioTranscription.query.filter_by(user_id=current_user.id).all()
    return render_template('dashboard.html', page_name='dashboard', files=user_files)

@transcription_bp.route('/start', methods=['POST'])
def start_recording():
    """
    Starts audio recording.

    Calls the 'start_recording_audio' method of the transcriber model to begin recording.
    """
    transcriber.start_recording_audio()
    return jsonify({"message": "Recording started"})

@transcription_bp.route('/pause', methods=['POST'])
def pause_recording():
    """
    Pauses the current audio recording.

    Calls the 'pause_recording_audio' method of the transcriber model to pause recording.
    """
    transcriber.pause_recording_audio()
    return jsonify({"message": "Recording paused"})

@transcription_bp.route('/stop', methods=['POST'])
def stop_recording():
    """
    Stops the audio recording and handles various actions based on the request.

    The function stops the recording, processes the audio file,
    and either saves it or deletes it based on the user's choice.
    Saving is done in the filesystem and referenced in the database.
    """
    data = request.get_json()
    action = data.get('action')

    # Stop recording and save audio
    audio_filepath, audio_save_successful = transcriber.stop_recording_audio()

    if action == "delete_audio":
        # If user chooses to delete audio, return a success status without a message
        return '', 204  # 204 No Content

    if audio_save_successful:
        # Process transcription if saving audio was successful
        stripped_audio_path = audio_filepath.replace('backend/static/', '')

        if action == "save_audio_and_transcribe":
            transcription_filepath, transcription_save_successful = transcriber.transcribe_raw_audio(audio_filepath)
            stripped_transcription_path = transcription_filepath.replace('backend/static/', '') if transcription_save_successful else None
        else:
            stripped_transcription_path = None

        # Save paths to the database for authenticated users
        if current_user.is_authenticated:
            audio_recording = AudioTranscription(
                audio_path=stripped_audio_path,
                transcription_path=stripped_transcription_path,
                user_id=current_user.id
            )
            db.session.add(audio_recording)
            db.session.commit()

            return jsonify({
                "audio_path": stripped_audio_path,
                "transcription_path": stripped_transcription_path,
            }), 201

        # Handle case when user is not authenticated
        return jsonify({"message": "User not authenticated"}), 401

    # Handle case when saving audio failed
    return jsonify({"success": False, "message": "Failed to save files."}), 500  # if an error occurs, trigger a prompt

@transcription_bp.route('/delete-all-files', methods=['POST'])
def delete_files():
    """
    Deletes all audio and transcription files for the authenticated user.

    This removes both the files from the file system and the corresponding database records.
    """
    try:
        # Query all records from the database of the current user
        all_files = AudioTranscription.query.filter_by(user_id=current_user.id).all()

        # Delete files from the local filesystem
        transcriber.delete_all_files(all_files, current_user.id)

        # Clear database records for the current user only
        db.session.query(AudioTranscription).filter_by(user_id=current_user.id).delete()
        db.session.commit()

        return jsonify({"success": True, "message": "All files deleted"})
    except Exception as e:
        print(f"Error during file deletion: {e}")
        return jsonify({"success": False, "message": "Failed to delete files"}), 500

@transcription_bp.route('/list-audio-files', methods=['GET'])
def list_audio_files():
    """
    Lists all audio file paths for the authenticated user.

    Queries the database for the user's audio recordings and returns their file paths in JSON format.
    """
    try:
        # Query the database for all audio recordings of the current user
        audio_recordings = AudioTranscription.query.filter_by(user_id=current_user.id).all()

        # Create a list of audio file paths (audio_path)
        audio_files = [recording.audio_path for recording in audio_recordings]

        return jsonify({'files': audio_files})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@transcription_bp.route('/list-transcription-files', methods=['GET'])
def list_transcription_files():
    """
    Lists all transcription file paths for the authenticated user.

    Queries the database for the user's transcription files and returns their paths in JSON format.
    """
    try:
        # Query the database for all transcription records
        audio_recordings = AudioTranscription.query.filter_by(user_id=current_user.id).all()

        # Create a list of transcription file paths (transcription_path)
        transcription_files = [recording.transcription_path for recording in audio_recordings if recording.transcription_path]

        return jsonify({'files': transcription_files})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@transcription_bp.route('/static/<path:filename>')
def serve_file(filename):
    """
    Serves static files from the 'static' folder.

    This route is used to retrieve and serve raw audio or transcription files from the server.
    """
    return send_from_directory('static', filename)
