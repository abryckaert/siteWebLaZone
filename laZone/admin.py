from flask import Blueprint, render_template, abort
from flask_login import login_required, current_user

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

@admin_bp.route('/')
@login_required
def homeAdmin():
    if not current_user.admin:
        abort(403)  
    return render_template('home.html', user=current_user)

