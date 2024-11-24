import os

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "secret-key")
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL", "sqlite:///audio_transcriber.db"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
