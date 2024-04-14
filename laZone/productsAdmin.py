from urllib.request import Request
from flask import Blueprint, Flask, abort, current_app, request, redirect, url_for, render_template, flash
from flask_login import current_user, login_required
from werkzeug.utils import secure_filename
import os

from .extensions import admin_required
from .extensions import db
from .models import Feedback, Product
from .models import Brand
from .models import Category
import time  

app = Flask(__name__)
product = Blueprint('productEdit', __name__, url_prefix='/admin/productEdit')

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

@product.route('/add_product', methods=['GET', 'POST'])
@login_required
@admin_required
def add_product():
    if request.method == 'POST':
        name = request.form['name']
        description = request.form.get('description', '')
        price = float(request.form['price'])
        stock = int(request.form['stock'])
        category_id = int(request.form['category_id'])
        brand_id = int(request.form['brand_id'])
        image = request.files['image_url']

        if image and allowed_file(image.filename):
            filename = secure_filename(image.filename)
            image_folder = os.path.join(current_app.root_path, 'static', 'productsImages')
            os.makedirs(image_folder, exist_ok=True)
            image_path = os.path.join(image_folder, filename)
            image.save(image_path)
            image_url = f"/static/productsImages/{filename}"
        else:
            flash("No image provided or incorrect file type!", "error")
            return render_template('addProductAdmin.html', categories=Category.query.all(), brands=Brand.query.all())

        new_product = Product(name=name, description=description, price=price, stock=stock, category_id=category_id, brand_id=brand_id, image_url=image_url)
        db.session.add(new_product)
        db.session.commit()
        flash("Product added successfully!", "success")
        return redirect(url_for('productEdit.list_product'))

    categories = Category.query.all()
    brands = Brand.query.all()
    return render_template('addProductAdmin.html', categories=categories, brands=brands)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg', 'gif'}

@product.route('/list_product', methods=['GET'])
@login_required
@admin_required
def list_product():
    products = Product.query.all()
    return render_template('listProductAdmin.html', products=products)

@login_required
@admin_required
@product.route('/edit_product/<int:product_id>', methods=['GET', 'POST'])
def edit_product(product_id):
    product = Product.query.get_or_404(product_id)
    categories = Category.query.all()
    brands = Brand.query.all()

    if request.method == 'POST':
        product.name = request.form['name']
        product.description = request.form['description']
        product.price = float(request.form['price'])
        product.stock = int(request.form['stock'])
        product.category_id = int(request.form['category_id'])
        product.brand_id = int(request.form['brand_id'])

        image_file = request.files['image_url']
        if image_file and allowed_file(image_file.filename):
            filename = secure_filename(image_file.filename)
            filepath = os.path.join(current_app.root_path, 'static', 'productsImages', filename)
            image_file.save(filepath)
            # Ajouter un timestamp ou un paramètre unique pour éviter le cache du navigateur
            product.image_url = f"/static/productsImages/{filename}?{int(time.time())}"
        
        db.session.commit()
        flash('Product updated successfully!', 'success')
        return redirect(url_for('productEdit.list_product'))

    return render_template('editProductAdmin.html', product=product, categories=categories, brands=brands)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg', 'gif'}

@product.route('/delete_comment/<int:comment_id>', methods=['POST'])
@login_required
@admin_required
def delete_comment(comment_id):
    comment = Feedback.query.get_or_404(comment_id)
    if comment:
        db.session.delete(comment)
        db.session.commit()
        flash("Comment deleted successfully.", "success")
    else:
        flash("Comment not found.", "error")
    return redirect(url_for('productEdit.list_comments'))

from flask import render_template
from .models import Feedback, Product

@product.route('/list_comments', methods=['GET'])
@login_required
@admin_required
def list_comments():
    comments = db.session.query(Feedback, Product).join(Product, Feedback.product_id == Product.id).all()
    return render_template('feedbackManagement.html', comments=comments)

@product.route('/edit_comment/<int:comment_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_comment(comment_id):
    feedback = Feedback.query.get_or_404(comment_id)
    if request.method == 'POST':
        feedback.content = request.form['content']
        db.session.commit()
        flash("Comment updated successfully.", "success")
        return redirect(url_for('productEdit.list_comments'))
    return render_template('editCommentAdmin.html', feedback=feedback)

@product.route('/admin/productEdit/delete_product/<int:product_id>', methods=['POST'])
@login_required
@admin_required
def delete_product(product_id):
    product = Product.query.get_or_404(product_id)
    db.session.delete(product)
    db.session.commit()
    flash('Produit supprimé avec succès.', 'success')
    return redirect(url_for('productEdit.list_product'))


