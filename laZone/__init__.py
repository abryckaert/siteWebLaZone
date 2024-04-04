from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os  

db = SQLAlchemy()

DB_NAME = "database.db"

def creation_App():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'jkzfjcfbnmjsnmzn'
    basedir = os.path.abspath(os.path.dirname(__file__))
    db_path = os.path.join(basedir, DB_NAME)

    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'    
    db.init_app(app)

    from .views import views
    from .auth import auth

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')

    from .models import User, Product, Order, OrderItem

    create_database(app)

    return app

def create_database(app):
    if not os.path.isfile(os.path.join(os.path.abspath(os.path.dirname(__file__)), DB_NAME)):
        with app.app_context():
            db.create_all()
        print('Created Database!')
