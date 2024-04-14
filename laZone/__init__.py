import os
from flask import Flask, abort, jsonify, render_template, request
from flask_login import LoginManager, current_user, login_required
from laZone.models import Brand, CartItem, Product
from .extensions import db  
from .admin import admin_bp
from .views import views
from .auth import auth
from .productsAdmin import product
from .products import product_blueprint
from .editProfile import edit
from .shoppingCart import shopping_cart_blueprint

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
    app.register_blueprint(product_blueprint, url_prefix='/product')
    app.register_blueprint(edit)
    app.register_blueprint(shopping_cart_blueprint  )


    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        from .models import User  
        return User.query.get(int(user_id))

    create_database(app)  

    @app.context_processor
    def inject_cart_count():
        if current_user.is_authenticated:
            cart_items = CartItem.query.filter_by(user_id=current_user.id).all()
            cart_count = sum(item.quantity for item in cart_items)
        else:
            cart_count = 0
        return {'cart_count': cart_count}
    
    @app.route('/search', methods=['GET'])
    def search():
        query = request.args.get('query', '')
        if not query:
            return render_template('listProduct.html', error="No search term provided.")

        product_results = Product.query.filter(Product.name.ilike('%' + query + '%')).all()
        brand_results = Brand.query.filter(Brand.name.ilike('%' + query + '%')).all()

        from markupsafe import escape
        messageAction = 'Resultat de votre recherche "' + escape(query) + '"'
        
        return render_template('listProduct.html', products=product_results, messageAction=messageAction)
    return app

def create_database(app):
    with app.app_context():
        if not os.path.exists(DB_NAME):
            db.create_all()
            print('Created Database!')


