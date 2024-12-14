import os
from sqlite3 import IntegrityError
from flask import Blueprint,render_template
from flask_login import login_required, current_user
from src.model.transcriber import Model
from src.database import db
from src.database.models import AudioTranscription
from src.control import actions
from flask import jsonify, request

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
    Endpoint for storing and analyzing an audio file.

    This endpoint handles the uploading of an audio file, stores it in the file system,
    triggers the transcription of the audio, performs an analysis on the transcription,
    and stores the related information in the database.

    Request Payload:
        - An audio file (under the key 'audio') must be provided in the form-data of the POST request.

    Returns:
        JSON Response:
            - Success: If the file is stored and analyzed successfully, returns a success message,
              along with a new value for a dropdown in the frontend.
            - Error (422): If the audio file is not provided or the file is invalid.
            - Error (500): For any unexpected errors during transcription, analysis, or saving to the database.
    """

    # Check if the request has the file part
    if 'audio' not in request.files:
        return jsonify({"error": "Invalid Audio File or Name"}), 422

    file = request.files['audio']

    try:
        # Store the audio file
        audio_filepath = actions.store_audio(file, db)
        # Trigger analysis of the audio file
        actions.transcribe_and_analyse(transcriber, current_user, db, audio_filepath)
        return jsonify({"success": True,
                        "message": "Transcription and Analysis successful",
                        "dropdown_value": audio_filepath}), 201 # Return success response with new dropdown value
    except IOError as e:
        return jsonify({"error": str(e)}), 422 # Catch error for storage of the audio file
    except RuntimeError as e:
        return jsonify({"error": str(e)}), 500 # Catch error during transcription or unexpected errors
    except ValueError as e:
        return jsonify({"error": str(e)}), 500 # Catch error during analysis creation
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@transcription_bp.route('/delete-all-files', methods=['POST'])
def delete_all_files():
    """
    Endpoint for deletion of ALL files.

    This function triggers the deletion of all files from the current user from the file system and database.

    Request Payload (JSON):
        None

    Returns:
        Response (JSON):
            - Success message with HTTP status 200 if the files are deleted successfully.
            - Error message with HTTP status 500 if an exception occurs during the deletion process.
    """
    try:
        actions.cleanup(current_user, db)
        return jsonify({"success": True, "message": "All files deleted successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@transcription_bp.route('/delete-file', methods=['POST'])
def delete_file():
    """
    Endpoint for deleting a single audio file and its associated data.

    This endpoint triggers the deletion of a single audio file and all its related data (e.g., transcription,
    analysis graphics) from both the file system and the database for the current authenticated user. The
    audio file is identified by its 'audio_filepath', and all related records are removed accordingly.

    Request Payload (JSON):
        {
            "filePath": "src/static/output/raw_audio/"
        }

    Returns:
        Response (JSON):
            - Success message with HTTP status 200 if the file is deleted successfully.
            - Error message with HTTP status 500 if an exception occurs during the deletion process.
    """
    try:
        data = request.json
        audio_filepath = data.get('filePath')
        actions.cleanup(current_user, db, audio_filepath)
        return jsonify({"success": True, "message": "Single file deleted successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@transcription_bp.route('/list-files', methods=['GET'])
def list_files():
    """
    Endpoint to list all audio, transcription, and improved text file paths for the authenticated user.

    This function retrieves all relevant file paths (audio, transcription, and improved text) and
    their corresponding creation timestamps from the database for the currently authenticated user.
    It returns this information in JSON format.

    Returns:
        Response: A JSON object containing:
            - 'audio_files': List of paths to the audio files.
            - 'transcription_files': List of paths to the transcription files.
            - 'improved_text_files': List of paths to the improved text files.
            - 'date_times': List of timestamps when the files were created.

        If an error occurs, a JSON response with an 'error' message and a 500 HTTP status code is returned.
    """
    try:
        # Call the function from actions.py to get the file paths
        files_data = actions.get_user_files(current_user)

        # Return the data as JSON
        return jsonify({'data': files_data}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@transcription_bp.route('/get-analytics', methods=['POST'])
def get_analytics():
    """
    Endpoint for retrieving analytics data for a specific audio recording.

    This endpoint processes a POST request to extract and return various analytics
    related to a specified audio recording. The data includes paths to transcription
    files, graphical analysis (e.g., pitch, energy, speech speed), and other relevant
    audio details stored in the database. The request must contain the file path of
    the audio recording in the request body.

    The audio file is identified by its `recording` file path, which must be provided
    in the JSON payload. If the file path is not provided, or if there is an error
    during the process, an appropriate error message will be returned.

    Args:
        None. The audio file path is provided in the JSON body of the POST request
        under the key "recording".

    Returns:
        Response (JSON):
            - On success: A JSON object containing the requested analytics data under
              the 'data' key, along with an HTTP status code of 200.
            - On error: A JSON object containing an error message, with an appropriate
              HTTP status code (400 for missing recording, 500 for server errors).
    """

    try:
        data = request.get_json()
        audio_filepath = data.get('recording')

        if not audio_filepath:
            return jsonify({'error': 'Recording not specified'}), 400

        # Call the function from actions.py to get the analytics
        analytics = actions.get_analytics(audio_filepath, db)

        # Return the data as JSON
        return jsonify({'data': analytics}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

