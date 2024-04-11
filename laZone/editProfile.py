import os
from flask import Blueprint, render_template, request, flash, redirect, url_for, current_app
from flask_login import login_required, current_user
from werkzeug.security import generate_password_hash
from werkzeug.utils import secure_filename

from .extensions import db
from .models import User
from laZone.productsAdmin import allowed_file  

edit = Blueprint('edit', __name__, url_prefix='/')

@edit.route('/editProfile', methods=['GET', 'POST'])
@login_required
def editProfile():
    if request.method == 'POST':
        current_user.first_name = request.form.get('first_name', current_user.first_name)
        new_password = request.form.get('password')

        if new_password:
            current_user.password = generate_password_hash(new_password)

        new_image_file = request.files.get('image_url')
        if new_image_file and new_image_file.filename:  
            if allowed_file(new_image_file.filename):
                filename = secure_filename(new_image_file.filename)
                image_folder = os.path.join(current_app.root_path, 'static', 'userImages')
                os.makedirs(image_folder, exist_ok=True)  
                image_path = os.path.join(image_folder, filename)
                new_image_file.save(image_path)
                current_user.profil_image_url = f"/static/userImages/{filename}"
                flash('Image updated successfully!', 'success')
            else:
                flash('Invalid image format.', 'error')

        db.session.commit()
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('edit.editProfile'))

    return render_template('editProfile.html', user=current_user)
