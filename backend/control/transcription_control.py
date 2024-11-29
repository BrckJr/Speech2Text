import os
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
    user_files = AudioTranscription.query.filter_by(user_id=current_user.id).all()
    return render_template('dashboard.html', page_name='dashboard', files=user_files)

@transcription_bp.route('/start', methods=['POST'])
def start_recording():
    transcriber.start_recording_audio()
    return jsonify({"message": "Recording started"})

@transcription_bp.route('/pause', methods=['POST'])
def pause_recording():
    transcriber.pause_recording_audio()
    return jsonify({"message": "Recording paused"})

@transcription_bp.route('/stop', methods=['POST'])
def stop_recording():
    # Get the user's choice from the request body
    data = request.get_json()
    transcribe = data.get('transcribe', False)

    # Stop recording
    audio_filepath, audio_save_successful = transcriber.stop_recording_audio()

    if audio_save_successful:
        # Remove '/backend/static/' part of the path for both audio and transcription to be compliant with Flask
        stripped_audio_path = audio_filepath.replace('backend/static/', '')

        if transcribe:
            transcription_filepath, transcription_save_successful = transcriber.transcribe_raw_audio(audio_filepath)
            if transcription_save_successful:
                stripped_transcription_path = transcription_filepath.replace('backend/static/', '')
            else:
                stripped_transcription_path = None
        else:
            stripped_transcription_path = None

        # Ensure the user is logged in
        if current_user.is_authenticated:
            # Save to the database
            audio_recording = AudioTranscription(
                audio_path=stripped_audio_path,
                transcription_path=stripped_transcription_path,
                user_id=current_user.id  # Associate the recording with the logged-in user
            )
            db.session.add(audio_recording)
            db.session.commit()

            return jsonify({"message": "Recording stopped and saved"})
        else:
            return jsonify({"message": "User not authenticated"}), 401

    # Handle case where the recording was not saved successfully
    return jsonify({"message": "Recording failed. It might be too short."}), 400


@transcription_bp.route('/delete-all-files', methods=['POST'])
def delete_files():
    try:
        # Query all records from the database of the current user
        all_files = AudioTranscription.query.filter_by(user_id=current_user.id).all()

        # Delete files from the local filesystem
        for file in all_files:
            if os.path.exists(file.audio_path):
                os.remove(file.audio_path)
            if file.transcription_path and os.path.exists(file.transcription_path):
                os.remove(file.transcription_path)

        # Clear database records for the current user only
        db.session.query(AudioTranscription).filter_by(user_id=current_user.id).delete()
        db.session.commit()

        return jsonify({"success": True, "message": "All files deleted"})
    except Exception as e:
        print(f"Error during file deletion: {e}")
        return jsonify({"success": False, "message": "Failed to delete files"}), 500

@transcription_bp.route('/list-audio-files', methods=['GET'])
def list_audio_files():
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
    """ Serve static files from the 'static' folder """

    return send_from_directory('static', filename)