from src.database import db
from datetime import datetime
from flask_login import UserMixin

class AudioTranscription(db.Model):
    """
    Represents an audio recording and its associated metadata, transcription, and analyses.

    This model stores information about an uploaded audio file, its transcription,
    associated analysis results, and metadata like timestamps, language, and word count.
    It is linked to a specific user via a foreign key relationship.

    Attributes:
        id (int): Unique identifier for each audio transcription record.
        audio_path (str): File path to the uploaded audio file (.wav).
        transcription_path (str): File path to the generated transcription file (.txt). None if not yet generated.
        created_at (datetime): Timestamp indicating when the transcription was created.
        user_id (int): Foreign key linking to the user who owns the transcription.
        speech_speed_graphic_path (str): File path to the speech speed analysis graphic. None if not available.
        pitch_graphic_path (str): File path to the pitch analysis graphic. None if not available.
        energy_graphic_path (str): File path to the energy analysis graphic. None if not available.
        improved_text_path (str): File path to the AI-improved text. None if not available.
        title (str): AI-generated title for the transcription. None if not yet generated.
        language (str): Language of the audio and transcription. None if not specified.
        audio_length (float): Duration of the audio in seconds. None if not calculated.
        word_count (int): Total number of words in the transcription. None if not calculated.
        summary (str): AI-generated summary of the transcription. None if not available.

    Methods:
        __repr__(): Returns a string representation of the AudioTranscription object.
    """
    __tablename__ = "audio_transcriptions"

    id = db.Column(db.Integer, primary_key=True)  # Unique ID for each recording
    user_id = db.Column(db.Integer, db.ForeignKey('user_index.id'), nullable=False)  # Corresponding User ID
    audio_path = db.Column(db.String(200), nullable=False, unique=True)  # Unique path to the .wav file
    transcription_path = db.Column(db.String(200), nullable=True, unique=True)  # Unique path to the .txt transcription
    created_at = db.Column(db.DateTime, nullable=False)  # Timestamp when the audio recording was created
    speech_speed_graphic_path = db.Column(db.String(200), nullable=True)  # Path to speech speed analysis graphic
    pitch_graphic_path = db.Column(db.String(200), nullable=True)  # Path to pitch analysis graphic
    energy_graphic_path = db.Column(db.String(200), nullable=True)  # Path to energy analysis graphic
    improved_text_path = db.Column(db.String(200), nullable=True)  # Path to AI-improved text
    title = db.Column(db.String(200), nullable=True)  # AI-generated title for the transcription
    language = db.Column(db.String(200), nullable=True)  # Language of the audio and transcription
    audio_length = db.Column(db.Float, nullable=True)  # Length of the audio in seconds
    word_count = db.Column(db.Integer, nullable=True)  # Word count in the transcription
    summary = db.Column(db.String(3000), nullable=True)  # AI-generated summary of the transcription

    def __repr__(self):
        """
        Returns a string representation of the AudioTranscription object.

        Example:
            "<AudioTranscription id=1, audio_path='/path/to/audio.wav', user_id=42>"
        """
        return f"<AudioTranscription id={self.id}, audio_path={self.audio_path}, user_id={self.user_id}>"

class User(db.Model, UserMixin):
    """
    Represents a user in the application.

    This model stores user-specific information, including credentials and a relationship
    to the audio transcriptions uploaded by the user.

    Attributes:
        id (int): Unique identifier for the user.
        username (str): The username chosen by the user.
        email (str): The user's email address.
        password (str): The user's hashed password.
        recordings (list): List of AudioTranscription objects associated with the user.

    Methods:
        __repr__(): Returns a string representation of the User object.
    """
    __tablename__ = "user_index"

    id = db.Column(db.Integer, primary_key=True)  # Unique ID for the user
    username = db.Column(db.String(150), unique=True, nullable=False)  # User's username
    email = db.Column(db.String(150), unique=True, nullable=False)  # User's email address
    password = db.Column(db.String(200), nullable=False)  # User's hashed password
    recordings = db.relationship('AudioTranscription', backref='owner',
                                 lazy=True)  # List of transcriptions uploaded by the user

    def __repr__(self):
        """
        Returns a string representation of the User object.

        Example:
            "<User id=42, username='johndoe', email='johndoe@example.com'>"
        """
        return f"<User id={self.id}, username={self.username}, email={self.email}>"
