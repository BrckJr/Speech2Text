import os

class Config:
    # The secret key is used by Flask for session management and other cryptographic operations.
    # It's critical to use a strong and unique key in production to prevent security vulnerabilities.
    # The default fallback "secret-key" should be replaced in production with a value set in the environment.
    SECRET_KEY = os.getenv("SECRET_KEY", "secret-key")

    # Database connection string. This determines how Flask-SQLAlchemy connects to the database.
    # It defaults to a local SQLite database file "audio_transcriber.db" for development.
    # In production, ensure a proper DATABASE_URL (e.g., PostgreSQL, MySQL) is set in the environment.
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL", "sqlite:///audio_transcriber.db"
    )

    # Disables SQLAlchemy's event system for tracking object modifications.
    # Setting this to False reduces overhead but disables certain advanced features.
    # Recommended to keep it False unless absolutely necessary.
    SQLALCHEMY_TRACK_MODIFICATIONS = False
