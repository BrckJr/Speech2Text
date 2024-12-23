from flask import Flask, render_template, redirect, url_for
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, current_user

from control import transcription_bp
from config import Config
from backend.src.database import db
from routes import auth_blueprint

# Factory function to create the Flask app
def create_app():
    app = Flask(__name__, template_folder='frontend/src/templates', static_folder='frontend/src/static')
    app.config.from_object(Config)

    # Initialize extensions
    db.init_app(app)  # Initializes the database extension (Ensure `db` is properly defined in `src.database`)
    Migrate(app, db)  # Initialize Flask-Migrate (Ensure migration files are properly set up)
    bcrypt = Bcrypt(app)  # Initialize Flask-Bcrypt (Ensure it's used in user authentication and registration logic)

    # LoginManager configuration
    login_manager = LoginManager(app)
    login_manager.login_view = 'auth.login'  # Redirect to login page
    login_manager.login_message = 'Please log in to access this page.'

    @login_manager.user_loader
    def load_user(user_id):
        from models import User  # Import within function to avoid circular imports
        return db.session.get(User, int(user_id))  # Ensure `User` model has a `get` method that works with `db.session`

    # Register blueprints
    app.register_blueprint(transcription_bp)  # Ensure `transcription_bp` is correctly defined in `transcription_control`
    app.register_blueprint(auth_blueprint)  # Ensure `auth_blueprint` is correctly defined in `auth.routes`

    return app

# Create the app
app = create_app()

# Default route for serving the HTML
@app.route('/')
def index():
    # If the user is authenticated, show the dashboard
    if current_user.is_authenticated:
        return render_template('dashboard.html', page_name='dashboard')

    # If not logged in, redirect to the public landing page
    return redirect(url_for('auth.landing_page'))

if __name__ == "__main__":
    app.run(debug=True)  # NOTE: Avoid using debug mode in production!