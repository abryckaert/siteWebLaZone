from flask import Blueprint, app, flash, redirect, render_template, url_for
from flask_login import login_required, current_user
from .extensions import db
from .models import CartItem, Product


shopping_cart_blueprint = Blueprint('shopping_cart', __name__, url_prefix='/shopping_cart')

@shopping_cart_blueprint.route('/', methods=['GET'])
@login_required
def view_cart():
    cart_items = CartItem.query.filter_by(user_id=current_user.id).all()
    total_price = sum(item.product.price * item.quantity for item in cart_items)
    return render_template('shoppingCart.html', cart_items=cart_items, total_price=total_price)

@shopping_cart_blueprint.route('/remove_item/<int:item_id>', methods=['POST'])
@login_required
def remove_item(item_id):
    item = CartItem.query.get_or_404(item_id)
    if item.user_id == current_user.id:
        db.session.delete(item)
        db.session.commit()
        flash('Item removed successfully', 'success')
    else:
        flash('Unauthorized action', 'error')
    return redirect(url_for('shopping_cart.view_cart'))


