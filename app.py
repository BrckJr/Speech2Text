from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

class AudioView:
    """
    A Flask-based application for simulating audio recording functionality.

    This class sets up routes and renders HTML templates to provide the
    user interface for starting/stopping audio recording and displaying prompts.
    """

    def __init__(self):
        self.is_recording = False

    def setup_routes(self):
        @app.route('/')
        def index():
            """
            Renders the main interface for the transcriber.
            """
            return render_template('index.html', is_recording=self.is_recording)

        @app.route('/start-recording', methods=['POST'])
        def start_recording():
            """
            Starts the audio recording process.
            """
            self.is_recording = True
            return jsonify({"message": "Recording started", "is_recording": self.is_recording})

        @app.route('/stop-recording', methods=['POST'])
        def stop_recording():
            """
            Stops the audio recording process.
            """
            self.is_recording = False
            return jsonify({"message": "Recording stopped", "is_recording": self.is_recording})

        @app.route('/show-transcription-prompt', methods=['GET'])
        def show_transcription_prompt():
            """
            Simulates a transcription prompt for user input.
            """
            return jsonify({"prompt": "Recording has been saved. Would you like to transcribe it?"})

# Instantiate the view
audio_view = AudioView()
audio_view.setup_routes()

if __name__ == '__main__':
    app.run(debug=True)
