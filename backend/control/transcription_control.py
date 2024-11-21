from flask import Blueprint, jsonify
from backend.model.transcriber import Model

# Create a Blueprint for transcription routes
transcription_bp = Blueprint('transcription', __name__)

# Create an instance of the model which executes the actual logic
transcriber = Model()

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
    transcriber.stop_recording_audio()
    return jsonify({"message": "Recording stopped"})

@transcription_bp.route('/delete-files', methods=['POST'])
def delete_files():
    transcriber.delete_all_files()
    return jsonify({"message": "All files deleted"})
