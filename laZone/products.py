from flask import Blueprint, Flask, render_template
from flask_login import current_user
from .extensions import db
from .models import Product, Category

app = Flask(__name__)
product_blueprint = Blueprint('product', __name__, url_prefix='/product')

@product_blueprint.route('/list_product', methods=['GET'])
def list_all_products():
    products = Product.query.all()
    if current_user.admin:
        return render_template('listProductAdmin.html', products=products)
    return render_template('listProduct.html', products=products)

@product_blueprint.route('/skateboard', methods=['GET'])
def list_skateboard_products():
    products = Product.query.join(Category).filter(Category.name == 'Skateboard').all()
    if current_user.admin:
        return render_template('listProductAdmin.html', products=products)
    return render_template('listProduct.html', products=products)

@product_blueprint.route('/casquettes', methods=['GET'])
def list_casquettes_products():
    products = Product.query.join(Category).filter(Category.name == 'Casquette').all()
    if current_user.admin:
        return render_template('listProductAdmin.html', products=products)
    return render_template('listProduct.html', products=products)

@product_blueprint.route('/chaussures', methods=['GET'])
def list_chaussures_products():
    products = Product.query.join(Category).filter(Category.name == 'Chaussures').all()
    if current_user.admin:
        return render_template('listProductAdmin.html', products=products)
    return render_template('listProduct.html', products=products)

@product_blueprint.route('/chaussettes', methods=['GET'])
def list_chaussettes_products():
    products = Product.query.join(Category).filter(Category.name == 'Chaussettes').all()
    if current_user.admin:
        return render_template('listProductAdmin.html', products=products)
    return render_template('listProduct.html', products=products)

@product_blueprint.route('/productDetail/<int:product_id>', methods=['GET'])
def productDetail(product_id):
    product = Product.query.get_or_404(product_id)
    return render_template('productDetail.html', product=product)

