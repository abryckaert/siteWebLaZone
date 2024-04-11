import os
from flask import Flask
from flask_login import LoginManager
from .extensions import db  
from .admin import admin_bp
from .views import views
from .auth import auth
from .productsAdmin import product
from .products import product_blueprint
from .editProfile import edit

DB_NAME = "database.db"

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'UneCleParDefautSecrète')  # Utilisation de variables d'environnement pour la clé secrète
    basedir = os.path.abspath(os.path.dirname(__file__))
    db_path = os.path.join(basedir, DB_NAME)
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
    
    db.init_app(app)  

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')
    app.register_blueprint(product)  
    app.register_blueprint(admin_bp)
    app.register_blueprint(product_blueprint)  
    app.register_blueprint(edit)


    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        from .models import User  
        return User.query.get(int(user_id))

    create_database(app)  

    return app

def create_database(app):
    """Crée la base de données si elle n'existe pas déjà."""
    with app.app_context():
        if not os.path.exists(DB_NAME):
            db.create_all()
            print('Created Database!')
