from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required
from flask_bcrypt import Bcrypt

from backend.database.models import User, db
from backend.auth.forms import RegistrationForm, LoginForm

auth_blueprint = Blueprint('auth', __name__)
bcrypt = Bcrypt()

@auth_blueprint.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()

    if form.validate_on_submit():
        # Check if the email is already taken
        existing_user = User.query.filter_by(email=form.email.data).first()
        if existing_user:
            flash('Email already exists. Please log in.', 'danger')
            return redirect(url_for('auth.login'))  # Redirect to login if user exists

        # Create new user and add to database
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()

        flash('Your account has been created! You can now log in.', 'success')
        return redirect(url_for('auth.login'))  # Redirect to login after successful registration

    return render_template('register.html', form=form, page_name='register')

@auth_blueprint.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()  # Assuming you're using Flask-WTF for form validation

    if form.validate_on_submit():
        # Retrieve user from database based on email
        user = User.query.filter_by(email=form.email.data).first()

        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user)
            flash('Login successful!', 'success')
            return redirect(url_for('index'))  # Redirect to the main page after login
        else:
            flash('Login unsuccessful. Please check your email and password.', 'danger')

    return render_template('login.html', form=form, page_name='login')  # Render the login template

@auth_blueprint.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))
