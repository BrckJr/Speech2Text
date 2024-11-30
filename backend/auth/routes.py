from flask import Blueprint, render_template, redirect, url_for, flash, session
from flask_login import login_user, logout_user, login_required
from flask_bcrypt import Bcrypt

from backend.database.models import User, db
from backend.auth.forms import RegistrationForm, LoginForm

# Blueprint for authentication-related routes
auth_blueprint = Blueprint('auth', __name__)

# Instance of Bcrypt for hashing passwords
bcrypt = Bcrypt()

@auth_blueprint.route('/register', methods=['GET', 'POST'])
def register():
    """
    Handles user registration by validating the form, checking if the email is already taken,
    creating a new user in the database, and redirecting to log in after successful registration.

    If the form is invalid or the email already exists, an appropriate message is displayed.
    """
    form = RegistrationForm()

    if form.validate_on_submit():
        # Check if the email is already taken
        existing_user = User.query.filter_by(email=form.email.data).first()
        if existing_user:
            flash('Email already exists. Please log in or register with a different email.', 'danger')
            return redirect(url_for('auth.login'))  # Redirect to login if user exists

        # Create new user and add to database
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()

        flash('Your account has been created! Please log in.', 'success')
        return redirect(url_for('auth.login'))  # Redirect to login after successful registration

    # Check if the email format is invalid
    if form.email.errors:
        flash(f"Invalid email address. Please provide a valid one.", 'danger')

    # Render the registration page with the form
    return render_template('register.html', form=form, page_name='register')

@auth_blueprint.route('/login', methods=['GET', 'POST'])
def login():
    """
    Handles user login by validating the form, checking the user's credentials,
    and redirecting to the home page after a successful login.

    If login fails, an error message is shown.
    """
    form = LoginForm()  # Assuming you're using Flask-WTF for form validation

    if form.validate_on_submit():
        # Retrieve user from the database based on email
        user = User.query.filter_by(email=form.email.data).first()

        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user)  # Log the user in
            flash('Login successful!', 'success')
            return redirect(url_for('index'))  # Redirect to the main page after login
        else:
            flash('Login failed. Please check your credentials.', 'danger')

    # Check if the email format is invalid
    if form.email.errors:
        flash(f"Invalid email address. Please provide a valid one.", 'danger')

    # Render the login page with the form
    return render_template('login.html', form=form, page_name='login')  # Render the login template

@auth_blueprint.route('/logout', methods=['POST'])
@login_required
def logout():
    """
    Logs the user out, clears any flash messages, and redirects to the login page.

    Requires the user to be logged in to access the route.
    """
    logout_user()  # Log out the current user
    session.pop('_flashes', None)  # Clear any stored flash messages
    # Optionally, you could add a message like: flash('You have been logged out successfully.', 'info')
    return redirect(url_for('auth.login'))  # Redirect to the login page