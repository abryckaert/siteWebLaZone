from flask import Blueprint, app, flash, redirect, render_template, url_for
from flask_login import login_required, current_user
from .extensions import admin_required, db
from .models import CartItem, Order, OrderItem, Product
from datetime import datetime


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


@shopping_cart_blueprint.route('/pay', methods=['POST'])
@login_required
def pay():
    cart_items = CartItem.query.filter_by(user_id=current_user.id).all()
    if not cart_items:
        flash("Your cart is empty.", "warning")
        return redirect(url_for('shopping_cart.view_cart'))

    total_price = sum(item.product.price * item.quantity for item in cart_items)
    new_order = Order(user_id=current_user.id, total_price=total_price, status='Completed', date_placed=datetime.utcnow())
    db.session.add(new_order)
    db.session.flush()  

    for item in cart_items:
        if item.product.stock >= item.quantity:
            order_item = OrderItem(order_id=new_order.id, product_id=item.product_id, quantity=item.quantity, price=item.product.price)
            db.session.add(order_item)
            item.product.stock -= item.quantity
        else:
            flash(f"Not enough stock for {item.product.name}.", "error")
            db.session.rollback()
            return redirect(url_for('shopping_cart.view_cart'))

    for item in cart_items:
        db.session.delete(item)

    db.session.commit()
    flash("Your order has been placed successfully!", "success")
    return redirect(url_for('shopping_cart.order_details', order_id=new_order.id))

@shopping_cart_blueprint.route('/orders', methods=['GET'])
@login_required
def list_orders():
    orders = Order.query.filter_by(user_id=current_user.id).order_by(Order.date_placed.desc()).all()
    return render_template('listOrders.html', orders=orders)

@shopping_cart_blueprint.route('/order_details/<int:order_id>', methods=['GET'])
@login_required
def order_details(order_id):
    order = Order.query.get_or_404(order_id)
    return render_template('orderDetails.html', order=order)


@shopping_cart_blueprint.route('/orders_admin', methods=['GET'])
@login_required
@admin_required
def list_orders_admin():
    orders = Order.query.order_by(Order.date_placed.desc()).all()
    return render_template('listOrders.html', orders=orders)
