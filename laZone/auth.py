from datetime import datetime, timedelta, timezone
from .extensions import limiter
from flask import Blueprint, app, redirect, render_template, request, flash, session, url_for, current_app
from flask_login import login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from .models import User
from .extensions import db


auth = Blueprint('auth', __name__)

login_attempts_by_ip = {}

@auth.route('/login', methods=['GET', 'POST'])
def login():
    ip = request.remote_addr  
    if ip not in login_attempts_by_ip:
        login_attempts_by_ip[ip] = {'count': 0, 'lockout_time': None}

    if login_attempts_by_ip[ip]['lockout_time']:
        if datetime.now() < login_attempts_by_ip[ip]['lockout_time']:
            lockout_minutes = (login_attempts_by_ip[ip]['lockout_time'] - datetime.now()).total_seconds() / 60
            flash(f'Please retry in {int(lockout_minutes)} minutes due to repeated login failures.', 'error')
            return render_template("login.html")

    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password):
            login_attempts_by_ip[ip] = {'count': 0, 'lockout_time': None}  
            login_user(user, remember=True)
            return redirect(url_for('views.home'))  
        else:
            login_attempts_by_ip[ip]['count'] += 1
            if login_attempts_by_ip[ip]['count'] >= 3:
                lockout_minutes = 5 * (2 ** (login_attempts_by_ip[ip]['count'] - 3))  
                login_attempts_by_ip[ip]['lockout_time'] = datetime.now() + timedelta(minutes=lockout_minutes)
            flash('Invalid credentials. Please try again.', 'error')

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
            login_user(new_user, remember=True)  
            flash('Account created!', category='success')
            return redirect(url_for('views.home'))
    
    return render_template("sign_up.html")
