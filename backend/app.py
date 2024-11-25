from flask import Flask, render_template
from flask_migrate import Migrate  # Import Flask-Migrate
from backend.control.transcription_control import transcription_bp
from backend.config import Config
from backend.database import db


# Factory function to create the Flask app
def create_app():
    app = Flask(__name__, template_folder='templates', static_folder='static')
    app.config.from_object(Config)

    # Initialize extensions
    db.init_app(app)
    Migrate(app, db)  # Initialize Flask-Migrate

    # Register blueprints
    app.register_blueprint(transcription_bp)
    return app


# Create the app
app = create_app()


# Default route for serving the HTML
@app.route('/')
def index():
    return render_template('index.html')


if __name__ == "__main__":
    app.run(debug=True)
