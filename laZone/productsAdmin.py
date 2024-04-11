from flask import Blueprint, Flask, current_app, request, redirect, url_for, render_template, flash
from flask_login import login_required
from werkzeug.utils import secure_filename
import os
from .extensions import db
from .models import Product
from .models import Brand
from .models import Category

app = Flask(__name__)
product = Blueprint('productEdit', __name__, url_prefix='/admin/productEdit')

@product.route('/add_product', methods=['GET', 'POST'])
@login_required
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
def list_product():
    products = Product.query.all()
    return render_template('listProductAdmin.html', products=products)

@product.route('/edit_product/<int:product_id>', methods=['GET', 'POST'])
@login_required
def edit_product(product_id):
    product = Product.query.get_or_404(product_id)
    if request.method == 'POST':
        product.name = request.form['name']
        product.description = request.form['description']
        product.price = float(request.form['price'])
        product.stock = int(request.form['stock'])
        category_id = request.form['category_id']  # Assure-toi que c'est 'category_id' et que tu as ce champ dans ton formulaire
        category = Category.query.get(category_id)
        if not category:
            flash('Category not found.', 'error')
            return redirect(url_for('edit_product', product_id=product_id))
        
        product.category = category

        brand_id = request.form['brand_id']
        brand = Brand.query.get(brand_id)
        if not brand:
            flash('Brand not found.', 'error')
            return redirect(url_for('edit_product', product_id=product_id))
        
        product.brand = brand
        
        db.session.commit()
        flash('Product updated successfully!', 'success')
        return redirect(url_for('list_all_products'))
    else:
        return render_template('editProductAdmin.html', product=product)