from flask import abort
from flask_login import current_user, login_required
from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()

def admin_required(f):
    @login_required
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.admin:
            abort(403)  
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function