from datetime import datetime, timedelta, timezone
from flask import Blueprint, redirect, render_template, request, flash, session, url_for
from flask_login import login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from .models import User
from .extensions import db

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if 'login_attempts' not in session:
        session['login_attempts'] = 0
        session['lockout_time'] = None

    current_time = datetime.now(timezone.utc) 
    lockout_time = session.get('lockout_time')

    if lockout_time and current_time < lockout_time:
        remaining_lockout_minutes = (lockout_time - current_time).total_seconds() / 60
        flash(f'Accès temporairement bloqué en raison de trop de tentative échouée. Re essayez dans {int(remaining_lockout_minutes)} minutes.', 'error')
        return render_template("login.html")

    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password):
            session['login_attempts'] = 0
            session['lockout_time'] = None
            login_user(user, remember=True)
            return redirect(url_for('views.home'))
        else:
            session['login_attempts'] += 1
            if session['login_attempts'] >= 3:
                lockout_minutes = 5 * 2 ** (session['login_attempts'] - 3)  
                session['lockout_time'] = current_time + timedelta(minutes=lockout_minutes)
                flash(f'Trop de tentatives échouées. Veuillez réessayer dans {lockout_minutes} minutes.', 'error')
            else:
                flash('Email ou mot de passe incorrect.', 'error')


    return render_template("login.html")

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))

@auth.route('/sign-up', methods=['GET', 'POST'])
def sign_up():
    if request.method == 'POST':
        email = request.form.get('email')
        firstName = request.form.get('firstName')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')

        user = User.query.filter_by(email=email).first()
        if user:
            flash('Email already exists.', category='error')
        elif len(email) < 4:
            flash('Email must be greater than 3 characters.', category='error')
        elif len(firstName) < 2:
            flash('First name must be greater than 1 character.', category='error')
        elif password1 != password2:
            flash('Passwords don\'t match.', category='error')
        elif len(password1) < 7:
            flash('Password must be at least 7 characters.', category='error')
        else:
            new_user = User(email=email, first_name=firstName, password=generate_password_hash(password1), profil_image_url="/static/userImages/default.png")
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user, remember=True)  # Automatically log in the new user
            flash('Account created!', category='success')
            return redirect(url_for('views.home'))
    
    return render_template("sign_up.html")
