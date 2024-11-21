from flask import Flask, render_template
from backend.control.transcription_control import transcription_bp

app = Flask(__name__, template_folder='templates', static_folder='static')

# Register the transcription blueprint
app.register_blueprint(transcription_bp)

# Default route for serving the HTML
@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
