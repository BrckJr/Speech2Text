from backend.database import db
from datetime import datetime
from flask_login import UserMixin

class AudioTranscription(db.Model):
    """
    Represents an audio recording and its associated transcription.

    This model stores file paths for the .wav audio file and its corresponding
    .txt transcription. It also includes a creation timestamp and a foreign key
    relationship to the user who uploaded the files.

    Attributes:
        id (int): Unique identifier for each audio transcription record.
        audio_path (str): File path to the uploaded audio file (.wav).
        transcription_path (str): File path to the generated transcription file (.txt). None if not existent.
        created_at (datetime): Timestamp when the transcription was created.
        user_id (int): Foreign key linking to the user who owns the transcription.
    """
    __tablename__ = "audio_transcriptions"

    id = db.Column(db.Integer, primary_key=True)  # Unique ID for each recording
    audio_path = db.Column(db.String(200), nullable=False, unique=True)  # Unique path to the .wav file
    transcription_path = db.Column(db.String(200), nullable=True, unique=True)  # Unique path to the .txt transcription
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)  # Timestamp
    user_id = db.Column(db.Integer, db.ForeignKey('user_index.id'), nullable=False)  # Corresponding User ID

    def __repr__(self):
        """
        Returns a string representation of the AudioTranscription object.
        The string includes the ID, audio file path, and transcription file path.
        """
        return f"<AudioRecording id={self.id}, audio_path={self.audio_path}, transcription_path={self.transcription_path}>"

class User(db.Model, UserMixin):
    """
    Represents a user who can upload audio recordings and their transcriptions.

    This model includes user details (such as username, email, and password)
    and a relationship to the audio transcriptions uploaded by the user.

    Attributes:
        id (int): Unique identifier for the user.
        username (str): The username chosen by the user.
        email (str): The user's email address.
        password (str): The user's hashed password.
        recordings (list): A list of AudioTranscription objects associated with the user.
    """
    __tablename__ = "user_index"

    id = db.Column(db.Integer, primary_key=True)  # Unique ID for the user
    username = db.Column(db.String(150), unique=True, nullable=False)  # User's username
    email = db.Column(db.String(150), unique=True, nullable=False)  # User's email address
    password = db.Column(db.String(200), nullable=False)  # User's hashed password
    # Use the 'AudioTranscription' class to relate files to the user
    recordings = db.relationship('AudioTranscription', backref='owner', lazy=True)

    def __repr__(self):
        """
        Returns a string representation of the User object. The string includes the user's ID, username, and email.
        """
        return f"<User id={self.id}, username={self.username}, email={self.email}>"
