import os
from flask import Blueprint, jsonify, send_from_directory, request
from sympy.parsing.sympy_parser import TRANS

from backend.model.transcriber import Model

# Create a Blueprint for transcription routes
transcription_bp = Blueprint('transcription', __name__)

# Create an instance of the model which executes the actual logic
transcriber = Model()

# Path to the stored raw audio files and transcriptions
AUDIO_FOLDER = "backend/static/output/raw_audio"
TRANSCRIPTION_FOLDER = "backend/static/output/transcription"

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
    filepath, save_successful = transcriber.stop_recording_audio()

    # Conditionally perform transcription
    if save_successful and transcribe:
        transcriber.transcribe_raw_audio(filepath)

    return jsonify({"message": "Recording stopped"})

@transcription_bp.route('/delete-all-files', methods=['POST'])
def delete_files():
    try:
        transcriber.delete_all_files()
        return jsonify({"success": True, "message": "All files deleted"})
    except Exception as e:
        print(f"Error during file deletion: {e}")
        return jsonify({"success": False, "message": "Failed to delete files"}), 500


@transcription_bp.route('/list-audio-files', methods=['GET'])
def list_audio_files():
    try:
        # List all files in the audio folder
        files = os.listdir(AUDIO_FOLDER)
        files = [file for file in files if os.path.isfile(os.path.join(AUDIO_FOLDER, file))]
        return jsonify({'files': files})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@transcription_bp.route('/list-transcription-files', methods=['GET'])
def list_transcription_files():
    try:
        # List all files in the audio folder
        files = os.listdir(TRANSCRIPTION_FOLDER)
        files = [file for file in files if os.path.isfile(os.path.join(TRANSCRIPTION_FOLDER, file))]
        return jsonify({'files': files})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Serve static files from the 'static' folder
@transcription_bp.route('/static/<path:filename>')
def serve_file(filename):
    return send_from_directory('static', filename)