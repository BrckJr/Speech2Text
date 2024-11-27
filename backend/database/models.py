from backend.database import db
from datetime import datetime
from flask_login import UserMixin

class AudioTranscription(db.Model):
    """
    Represents an audio recording and its associated transcription.
    Stores file paths for the .wav audio file and the .txt transcription file.
    """
    __tablename__ = "audio_recordings"

    id = db.Column(db.Integer, primary_key=True)  # Unique ID for each recording
    audio_path = db.Column(db.String(200), nullable=False)  # Path to the .wav file
    transcription_path = db.Column(db.String(200), nullable=True)  # Path to the .txt transcription
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)  # Timestamp
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  # Corresponding User ID

    def __repr__(self):
        return f"<AudioRecording id={self.id}, audio_path={self.audio_path}, transcription_path={self.transcription_path}>"

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    # Use the 'AudioTranscription' class to relate files to the user
    recordings = db.relationship('AudioTranscription', backref='owner', lazy=True)

    def __repr__(self):
        return f"<User id={self.id}, username={self.username}, email={self.email}>"
