from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import current_user
from app.models import Product, Sale, Cashier
from app.utils.decorators import license_required

bp = Blueprint('main', __name__)

@bp.route('/')
@license_required
def index():
    return render_template('index.html')

@bp.route('/dashboard')
@license_required
def dashboard():
    # Obter estatísticas
    total_products = Product.query.count()
    total_sales = Sale.query.count()
    total_revenue = sum(sale.total_price for sale in Sale.query.all()) or 0

    # Calcular produtos com estoque baixo (20% ou menos do máximo histórico, ou menos de 5 unidades - o que for maior)
    # Exclui o produto especial para pagamento de fiado
    products = Product.query.filter(Product.name != 'Pagamento de Fiado').all()
    low_stock_products_list = []

    for product in products:
        # Calcular o limite de estoque baixo como 20% do estoque máximo ou 5, o que for maior
        low_threshold = max(5, int(product.max_quantity * 0.2)) if product.max_quantity > 0 else 5

        if product.quantity <= low_threshold:
            low_stock_products_list.append(product)

    low_stock_products = len(low_stock_products_list)

    # Últimas vendas
    recent_sales = Sale.query.order_by(Sale.sale_date.desc()).limit(5).all()

    # Obter caixa ativo do usuário
    active_cashier = Cashier.query.filter_by(user_id=current_user.id, status='open').first()

    return render_template(
        'dashboard.html',
        total_products=total_products,
        total_sales=total_sales,
        total_revenue=total_revenue,
        low_stock_products=low_stock_products,
        low_stock_products_list=low_stock_products_list,
        recent_sales=recent_sales,
        active_cashier=active_cashier
    )