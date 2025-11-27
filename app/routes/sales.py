from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import current_user
from app.models import Sale, Product, Cashier, CashierTransaction
from app import db
from app.utils.decorators import license_required
from datetime import datetime

bp = Blueprint('sales', __name__)

@bp.route('/sales')
@license_required
def list_sales():
    sales = Sale.query.all()
    return render_template('sales/list.html', sales=sales)

@bp.route('/sales/new', methods=['GET', 'POST'])
@license_required
def new_sale():
    products = Product.query.all()

    if request.method == 'POST':
        product_id = int(request.form.get('product_id'))
        quantity = int(request.form.get('quantity'))

        product = Product.query.get_or_404(product_id)

        if product.quantity < quantity:
            flash('Quantidade insuficiente em estoque!', 'error')
            return render_template('sales/form.html', products=products)

        total_price = product.price * quantity

        # Associar venda ao caixa ativo, se existir
        active_cashier = Cashier.query.filter_by(user_id=current_user.id, status='open').first()

        sale = Sale(
            product_id=product_id,
            quantity=quantity,
            total_price=total_price,
            cashier_id=active_cashier.id if active_cashier else None  # Associar diretamente ao caixa ativo
        )

        # Atualizar estoque
        product.quantity -= quantity
        product.update_max_quantity()  # Atualizar quantidade máxima se necessário

        db.session.add(sale)
        db.session.flush()  # Para obter o ID da venda antes do commit

        if active_cashier:
            # Atualizar total de vendas do caixa
            active_cashier.total_sales += total_price

            # Criar transação de caixa para a venda
            transaction = CashierTransaction(
                cashier_id=active_cashier.id,
                transaction_type='sale',
                amount=total_price,
                description=f'Venda - {product.name}',
                related_sale_id=sale.id
            )

            db.session.add(transaction)

        db.session.commit()

        flash('Venda registrada com sucesso!', 'success')
        return redirect(url_for('sales.list_sales'))

    return render_template('sales/form.html', products=products)