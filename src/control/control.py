import os
from flask import Blueprint, jsonify, send_from_directory, request, render_template
from flask_login import login_required, current_user
from src.model.transcriber import Model
from src.database import db
from src.database.models import AudioTranscription
from src.control import actions
from pydub import AudioSegment
from flask import jsonify, request
import src.utils.utils as utils
import time

# Create a Blueprint for transcription routes
transcription_bp = Blueprint('transcription', __name__)

# Create an instance of the model which executes the actual logic
transcriber = Model()

# Path to the stored raw audio files and transcriptions
AUDIO_FOLDER = "src/static/output/raw_audio/"
TRANSCRIPTION_FOLDER = "src/static/output/transcription/"

@transcription_bp.route('/dashboard')
@login_required
def dashboard():
    """
    Endpoint for displaying the main dashboard
    """
    return render_template('dashboard.html', page_name='dashboard')

@transcription_bp.route('/store_and_analyze', methods=['POST'])
def store_and_analyze():
    """
    Endpoint for storing and analyzing the audio files.

    Triggers the storage of the audio, analysis of the audio and storing of information in
    from the action file.
    """
    # start_time = time.time()  # Start the timer

    # Check if the request has the file part
    if 'audio' not in request.files:
        return jsonify({"error": "Invalid Audio File or Name"}), 422

    file = request.files['audio']
    filename = file.filename

    if filename == '':
        filename = utils.get_default_audio_filename()  # generate default filename

    # Base filename and extension
    base_name, extension = filename.rsplit('.', 1) if '.' in filename else (filename, '')

    # Generate a unique filename
    unique_filename = filename
    audio_filepath = f"{AUDIO_FOLDER}{filename}.wav"

    counter = 1
    while db.session.query(AudioTranscription).filter_by(audio_path=audio_filepath).first():
        unique_filename = f"{base_name}({counter}){'.' + extension if extension else ''}"
        audio_filepath = f"{AUDIO_FOLDER}{unique_filename}.wav"
        counter += 1

    # Save the file temporarily before processing
    temp_filepath = f"{AUDIO_FOLDER}temp_{unique_filename}.wav"
    try:
        file.save(temp_filepath)

        # Convert the file to .wav if it's not already a .wav
        if extension.lower() not in ['wav']:
            try:
                audio = AudioSegment.from_file(temp_filepath)
                audio.export(audio_filepath, format="wav")
                os.remove(temp_filepath)  # Remove the temporary file
            except Exception:
                return jsonify({"error": "Unsupported audio format or conversion failed"}), 404
        else:
            # If already a .wav file, just move it
            os.rename(temp_filepath, audio_filepath)

        # Trigger analysis of the audio file
        response, status_code = actions.transcribe_and_analyse(transcriber, current_user, db, audio_filepath)

        # End the timer and calculate elapsed time
        # elapsed_time = time.time() - start_time
        # print(f"Execution time for store_and_analyze: {elapsed_time:.2f} seconds")

        # Return success response
        return jsonify({"response": response, "dropdown_value": audio_filepath}), status_code

    except Exception as e:
        print(f"Error saving file: {e}")
        # elapsed_time = time.time() - start_time
        # print(f"Execution time for store_and_analyze (failed): {elapsed_time:.2f} seconds")
        return jsonify({"error": "Failed to save file"}), 500

@transcription_bp.route('/delete-all-files', methods=['POST'])
def delete_files():
    """
    Endpoint for deletion of ALL files for the currently authenticated user.
    """
    try:
        # Query all records from the database of the current user
        all_files = AudioTranscription.query.filter_by(user_id=current_user.id).all()

        # Delete files from the local filesystem
        actions.delete_files(all_files)

        # Clear database records for the current user only
        db.session.query(AudioTranscription).filter_by(user_id=current_user.id).delete()
        db.session.commit()

        return jsonify({"success": True, "message": "All files deleted"})
    except Exception:
        return jsonify({"success": False, "message": "Failed to delete all files"}), 500

@transcription_bp.route('/delete-file', methods=['POST'])
def delete_file():
    """
    Endpoint for deletion of a single recording and all connected files.

    The method receives the audio_filepath from the frontend, retrieves paths to all connected files from the
    database and deletes them in the file system as well as the respective row in the database.
    """
    try:
        data = request.json
        audio_filepath = data.get('filePath')
        if not audio_filepath:
            return jsonify({'success': False, 'error': 'File path is required'}), 400

        print(f"Inserted Filepath: {audio_filepath}")

        if os.path.exists(audio_filepath):
            # Query all records from the database connected to the selected audio recording
            all_files = AudioTranscription.query.filter_by(audio_path=audio_filepath).all()
            # Delete files from the local filesystem
            actions.delete_files(all_files)
            # Clear database records for the current file
            db.session.query(AudioTranscription).filter_by(audio_path=audio_filepath).delete()
            db.session.commit()
            return jsonify({'success': True})
        else:
            return jsonify({'success': False, 'error': 'File not found'}), 404
    except Exception as e:
        return jsonify({"success": False, "message": "Failed to delete file"}), 500

@transcription_bp.route('/list-files', methods=['GET'])
def list_files():
    """
    Endpoint to list all audio and transcription file paths for the authenticated user.

    Queries the database for the user's audio recordings and transcriptions, returning their full file paths in JSON format.
    """
    try:
        # Query the database for all audio recordings of the current user
        audio_recordings = AudioTranscription.query.filter_by(user_id=current_user.id).all()

        # Create a list of audio file paths
        audio_files = [recording.audio_path for recording in audio_recordings]

        # Create a list of transcription file paths
        transcription_files = [recording.transcription_path for recording in audio_recordings]#

        # Create a list of improved text file paths
        improved_text_files = [recording.improved_text_path for recording in audio_recordings]

        # Create a list of times when files where stored
        date_times = [recording.created_at for recording in audio_recordings]

        return jsonify({
            'audio_files': audio_files,
            'transcription_files': transcription_files,
            'improved_text_files': improved_text_files,
            'date_times': date_times
        })

    except Exception as e:
        return jsonify({'error': str(e), "message": "Error during loading of file lists."}), 500

@transcription_bp.route('/get-analytics', methods=['POST'])
def get_analytics():
    """
    Endpoint for getting the analytics data for the currently authenticated user.

    Extract the information or path to all relevant analysis aspects from the database
    and send it back to the frontend in JSON format.
    """

    try:
        data = request.get_json()
        audio_filepath = data.get('recording')

        if not audio_filepath:
            return jsonify({'error': 'Recording not specified'}), 400

        # Retrieve the relevant row in the database
        target_database_entry = db.session.query(AudioTranscription).filter_by(audio_path=audio_filepath).first()

        # Extract all information from the database
        if target_database_entry:
            created_at = target_database_entry.created_at
            transcribed_text_path = target_database_entry.transcription_path
            speech_speed_graphic_path = target_database_entry.speech_speed_graphic_path
            pitch_graphic_path = target_database_entry.pitch_graphic_path
            energy_graphic_path = target_database_entry.energy_graphic_path
            improved_text_path = target_database_entry.improved_text_path
            title = target_database_entry.title
            language = target_database_entry.language
            audio_length = target_database_entry.audio_length
            word_count = target_database_entry.word_count
            summary = target_database_entry.summary
            return jsonify({'success': True,
                            'created_at': created_at,
                            'transcribed_text_path': transcribed_text_path,
                            'speech_speed_graphic_path': speech_speed_graphic_path,
                            'pitch_graphic_path': pitch_graphic_path,
                            'energy_graphic_path': energy_graphic_path,
                            'improved_text_path': improved_text_path,
                            'recording_title': title,
                            'recording_language': language,
                            'audio_length': audio_length,
                            'word_count': word_count,
                            'text_summary': summary
                            }), 200
        else:
            return jsonify({'error': 'Requested audio file was not found in database'}), 404

    except Exception as e:
        return jsonify({'error': str(e), "message": "Error within execution of get analytics."}), 500

