from backend.database import db
from datetime import datetime


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

    def __repr__(self):
        return f"<AudioRecording id={self.id}, audio_path={self.audio_path}, transcription_path={self.transcription_path}>"