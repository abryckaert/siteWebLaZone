from flask import Blueprint, redirect, render_template, url_for
from flask_login import login_required, current_user
from .extensions import db
from .models import Product


views = Blueprint('views', __name__)

@views.route('/')
def home():
    products = Product.query.all()
    if not current_user.is_authenticated:
        return render_template("homeAnonymous.html", products=products)
    elif current_user.admin:
        return render_template("homeAdmin.html", user=current_user, products=products)
    return render_template("home.html", user=current_user, products=products)

