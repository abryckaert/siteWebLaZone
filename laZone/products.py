from datetime import datetime
from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required
from .extensions import db
from .models import CartItem, Favorite, Feedback, Product, Category

product_blueprint = Blueprint('product', __name__, url_prefix='/product')

@product_blueprint.route('/list_product', methods=['GET'])
def list_all_products():
    products = Product.query.all()
    if current_user.is_authenticated and current_user.admin:
        return render_template('listProductAdmin.html', products=products)
    return render_template('listProduct.html', products=products)

@product_blueprint.route('/skateboard', methods=['GET'])
def list_skateboard_products():
    products = Product.query.join(Category).filter(Category.name == 'Skateboards').all()
    if current_user.is_authenticated and current_user.admin:
        return render_template('listProductAdmin.html', products=products, messageAction="Nos skateboards")
    return render_template('listProduct.html', products=products, messageAction="Nos skateboards")

@product_blueprint.route('/casquettes', methods=['GET'])
def list_casquettes_products():
    products = Product.query.join(Category).filter(Category.name == 'Casquettes').all()
    if current_user.is_authenticated and current_user.admin:
        return render_template('listProductAdmin.html', products=products, messageAction="Nos Casquettes")
    return render_template('listProduct.html', products=products, messageAction="Nos Casquettes")

@product_blueprint.route('/chaussures', methods=['GET'])
def list_chaussures_products():
    products = Product.query.join(Category).filter(Category.name == 'Chaussures').all()
    if current_user.is_authenticated and current_user.admin:
        return render_template('listProductAdmin.html', products=products, messageAction="Nos Chaussures")
    return render_template('listProduct.html', products=products, messageAction="Nos Chaussures")

@product_blueprint.route('/chaussettes', methods=['GET'])
def list_chaussettes_products():
    products = Product.query.join(Category).filter(Category.name == 'Chaussettes').all()
    if current_user.is_authenticated and current_user.admin:
        return render_template('listProductAdmin.html', products=products, messageAction="Nos chaussettes")
    return render_template('listProduct.html', products=products, messageAction="Nos chaussettes")

@product_blueprint.route('/productDetail/<int:product_id>', methods=['GET'])
def productDetail(product_id):
    product = Product.query.get_or_404(product_id)
    feedbacks = Feedback.query.filter_by(product_id=product_id).order_by(Feedback.created_at.desc()).all()
    return render_template('productDetail.html', product=product, feedbacks=feedbacks)

@product_blueprint.route('/add_to_cart/<int:product_id>', methods=['POST'])
@login_required
def add_to_cart(product_id):
    product = Product.query.get_or_404(product_id)
    
    existing_cart_item = CartItem.query.filter_by(user_id=current_user.id, product_id=product.id).first()
    
    if existing_cart_item:
        existing_cart_item.quantity += 1
        flash("Quantité augmentée pour le produit dans le panier.", "success")
    else:
        if product.stock > 0:
            new_cart_item = CartItem(user_id=current_user.id, product_id=product.id, quantity=1)
            db.session.add(new_cart_item)
            flash("Produit ajouté au panier", "success")
        else:
            flash("Ce produit est en rupture de stock.", "error")
            return redirect(url_for('product.productDetail', product_id=product_id))
    
    db.session.commit()
    return redirect(url_for('product.productDetail', product_id=product_id))


@login_required
@product_blueprint.route('/add_comment/<int:product_id>', methods=['POST'])
def add_comment(product_id):
    if not current_user.is_authenticated:
        flash("Vous devez etre connecté pour mettre un commentaire.", "error")
        return redirect(url_for('product.productDetail', product_id=product_id))

    comment_content = request.form.get('comment')
    if not comment_content:
        flash("Les commentaires ne peuvent pas etre vides.", "error")
        return redirect(url_for('product.productDetail', product_id=product_id))
    
    new_feedback = Feedback(
        product_id=product_id,
        user_id=current_user.id,
        content=comment_content,
        created_at=datetime.utcnow()
    )
    db.session.add(new_feedback)
    db.session.commit()

    flash("Commentaire ajouté.", "success")
    return redirect(url_for('product.productDetail', product_id=product_id))

@product_blueprint.route('/delete_comment/<int:comment_id>', methods=['POST'])
@login_required
def delete_comment(comment_id):
    feedback = Feedback.query.get_or_404(comment_id)
    if current_user.id == feedback.user_id or current_user.admin:  
        db.session.delete(feedback)
        db.session.commit()
        flash('Commentaire suprimé.', 'success')
    else:
        flash('You do not have permission to delete this comment.', 'danger')
    return redirect(url_for('product.productDetail', product_id=feedback.product_id))

@product_blueprint.route('/add_to_favorite/<int:product_id>', methods=['POST'])
@login_required
def add_to_favorite(product_id):
    product = Product.query.get_or_404(product_id)
    
    existing_favorite = Favorite.query.filter_by(user_id=current_user.id, product_id=product.id).first()
    
    if existing_favorite:
        flash("Ce produit est déjà dans vos favoris.", "info")
    else:
        new_favorite = Favorite(user_id=current_user.id, product_id=product.id)
        db.session.add(new_favorite)
        flash("Produit ajouté aux favoris", "success")
    
    db.session.commit()
    return redirect(url_for('product.productDetail', product_id=product_id))

@product_blueprint.route('/remove_from_favorites/<int:favorite_id>', methods=['POST'])
@login_required
def remove_from_favorites(favorite_id):
    favorite = Favorite.query.get_or_404(favorite_id)
    if favorite:
        db.session.delete(favorite)
        db.session.commit()
        flash("Produit retiré des favoris.", "success")
    return redirect(url_for('product.display_favorites'))

@product_blueprint.route('/favorites', methods=['GET'])
@login_required
def display_favorites():
    favorites = Favorite.query.filter_by(user_id=current_user.id).join(Product, Favorite.product_id == Product.id).all()
    return render_template('userFavorite.html', favorites=favorites)