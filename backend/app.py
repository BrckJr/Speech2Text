from flask import Flask, render_template, redirect, url_for
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, current_user

from backend.control.transcription_control import transcription_bp
from backend.config import Config
from backend.database import db
from backend.auth.routes import auth_blueprint


# Factory function to create the Flask app
def create_app():
    app = Flask(__name__, template_folder='templates', static_folder='static')
    app.config.from_object(Config)

    # Initialize extensions
    db.init_app(app)
    Migrate(app, db)  # Initialize Flask-Migrate
    bcrypt = Bcrypt(app) # Initialize Flask-Bcrypt

    login_manager = LoginManager(app)
    login_manager.login_view = 'auth.login'  # Redirect to login page
    login_manager.login_message = 'Please log in to access this page.'

    @login_manager.user_loader
    def load_user(user_id):
        from backend.database.models import User
        return User.query.get(int(user_id))

    # Register blueprints
    app.register_blueprint(transcription_bp)
    app.register_blueprint(auth_blueprint)
    return app


# Create the app
app = create_app()


# Default route for serving the HTML
@app.route('/')
def index():
    # If the user is authenticated, show the main page (or dashboard)
    if current_user.is_authenticated:
        return render_template('dashboard.html', page_name='dashboard')  # Main page after login

    # If not logged in, redirect to the login page
    return redirect(url_for('auth.login'))  # Login route (change if it's a different route)

if __name__ == "__main__":
    app.run(debug=True)
