from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import current_user
from app.models import Sale, Product, Cashier, CashierTransaction
from app import db
from app.utils.decorators import license_required
from datetime import datetime
from flask_wtf import FlaskForm
import os

bp = Blueprint('sales', __name__)

class SalesForm(FlaskForm):
    class Meta:
        csrf = True
        csrf_secret = os.environ.get('SECRET_KEY', 'sua_chave_secreta_aqui').encode('utf-8')

@bp.route('/sales')
@license_required
def list_sales():
    sales = Sale.query.all()
    return render_template('sales/list.html', sales=sales)

@bp.route('/sales/new', methods=['GET', 'POST'])
@license_required
def new_sale():
    form = SalesForm()
    products = Product.query.all()

    # Verificar se o usuário tem caixa aberto (exceto gerentes/admins)
    active_cashier = Cashier.query.filter_by(user_id=current_user.id, status='open').first()
    is_manager = current_user.role == 'manager' or current_user.is_admin
    has_open_cashier = active_cashier is not None

    # Se não for gerente/admin e não tiver caixa aberto, mostrar mensagem persistente
    if not is_manager and not has_open_cashier:
        flash('Você precisa abrir o caixa antes de registrar uma venda.', 'warning')

    # Mostrar mensagem de erro se tentar registrar venda sem caixa aberto
    if request.method == 'POST':
        if not is_manager and not active_cashier:
            flash('Você precisa abrir o caixa antes de registrar uma venda.', 'error')
            return render_template('sales/form.html', products=products, form=form)

    if request.method == 'POST' and form.validate_on_submit():
        # Verificar se é uma venda múltipla ou única
        products_data = request.form.get('products_data')

        if products_data:
            # Processar venda múltipla
            import json
            try:
                products_list = json.loads(products_data)
            except json.JSONDecodeError:
                flash('Dados de produtos inválidos.', 'error')
                return render_template('sales/form.html', products=products, form=form)

            if not products_list:
                flash('Nenhum produto selecionado.', 'error')
                return render_template('sales/form.html', products=products, form=form)

            # Determinar se o usuário é gerente (pode vender com caixa fechado)
            is_manager = current_user.role == 'manager' or current_user.is_admin

            # Verificar se o caixa está aberto para usuários normais
            if not is_manager and not active_cashier:
                flash('Você precisa abrir o caixa antes de registrar uma venda.', 'error')
                return render_template('sales/form.html', products=products, form=form)

            # Verificar estoque e calcular totais
            total_sale_price = 0
            products_to_update = []

            for item in products_list:
                product_id = item['product_id']
                quantity = item['quantity']
                # Verificar se há desconto aplicado (vem do frontend)
                discount_percentage = item.get('discount_percentage', 0.0)

                product = Product.query.get_or_404(product_id)

                if product.quantity == 0:
                    flash(f'Item sem estoque: {product.name}', 'error')
                    return render_template('sales/form.html', products=products, form=form)
                elif product.quantity < quantity:
                    flash(f'Quantidade insuficiente em estoque para {product.name}!', 'error')
                    return render_template('sales/form.html', products=products, form=form)

                total_price = product.price * quantity
                discount_amount = (total_price * discount_percentage) / 100
                final_price = total_price - discount_amount
                total_sale_price += final_price  # Somar o preço final com desconto

                # Adicionar produto para atualização
                products_to_update.append({
                    'product': product,
                    'quantity': quantity,
                    'total_price': total_price,
                    'discount_percentage': discount_percentage,
                    'discount_amount': discount_amount,
                    'final_price': final_price
                })

            # Salvar todas as vendas
            sale_ids = []
            for item in products_to_update:
                product = item['product']
                quantity = item['quantity']
                total_price = item['total_price']
                discount_percentage = item['discount_percentage']
                discount_amount = item['discount_amount']
                final_price = item['final_price']

                sale = Sale(
                    product_id=product.id,
                    quantity=quantity,
                    total_price=total_price,
                    discount_percentage=discount_percentage,
                    discount_amount=discount_amount,
                    final_price=final_price,
                    cashier_id=active_cashier.id if active_cashier else None
                )

                # Atualizar estoque
                product.quantity -= quantity
                product.update_max_quantity()

                db.session.add(sale)
                db.session.flush()  # Para obter o ID da venda antes do commit
                sale_ids.append(sale.id)

                if active_cashier:
                    # Atualizar total de vendas do caixa com o preço final após desconto
                    active_cashier.total_sales += final_price

                    # Criar transação de caixa para a venda
                    transaction = CashierTransaction(
                        cashier_id=active_cashier.id,
                        transaction_type='sale',
                        amount=final_price,  # Usar o preço final após desconto
                        description=f'Venda - {product.name} (Desconto: {discount_percentage}%)',
                        related_sale_id=sale.id
                    )

                    db.session.add(transaction)

            db.session.commit()

            flash(f'{len(products_list)} vendas registradas com sucesso!', 'success')
            return redirect(url_for('sales.list_sales'))

        else:
            # Processar venda individual
            # Obter os dados da venda individual
            product_id_str = request.form.get('product_id')
            quantity_str = request.form.get('quantity')

            # Verificar se os campos obrigatórios existem e não estão vazios
            if not product_id_str or not quantity_str:
                flash('Por favor, selecione um produto e informe a quantidade.', 'error')
                return render_template('sales/form.html', products=products, form=form)

            try:
                product_id = int(product_id_str)
                quantity = int(quantity_str)
            except ValueError:
                flash('Dados inválidos para produto ou quantidade.', 'error')
                return render_template('sales/form.html', products=products, form=form)

            discount_percentage = float(request.form.get('discount_percentage', 0.0))  # Obter desconto do formulário

            product = Product.query.get_or_404(product_id)

            if product.quantity == 0:
                flash(f'Item sem estoque: {product.name}', 'error')
                return render_template('sales/form.html', products=products, form=form)
            elif product.quantity < quantity:
                flash('Quantidade insuficiente em estoque!', 'error')
                return render_template('sales/form.html', products=products, form=form)

            total_price = product.price * quantity
            discount_amount = (total_price * discount_percentage) / 100
            final_price = total_price - discount_amount

            # Verificar se o usuário pode registrar a venda com base no status do caixa
            active_cashier = Cashier.query.filter_by(user_id=current_user.id, status='open').first()

            # Determinar se o usuário é gerente (pode vender com caixa fechado)
            is_manager = current_user.role == 'manager' or current_user.is_admin

            # Verificar se o caixa está aberto para usuários normais
            if not is_manager and not active_cashier:
                flash('Você precisa abrir o caixa antes de registrar uma venda.', 'error')
                return render_template('sales/form.html', products=products, form=form)

            sale = Sale(
                product_id=product_id,
                quantity=quantity,
                total_price=total_price,
                discount_percentage=discount_percentage,
                discount_amount=discount_amount,
                final_price=final_price,
                cashier_id=active_cashier.id if active_cashier else None  # Associar diretamente ao caixa ativo
            )

            # Atualizar estoque
            product.quantity -= quantity
            product.update_max_quantity()  # Atualizar quantidade máxima se necessário

            db.session.add(sale)
            db.session.flush()  # Para obter o ID da venda antes do commit

            if active_cashier:
                # Atualizar total de vendas do caixa com o preço final após desconto
                active_cashier.total_sales += final_price

                # Criar transação de caixa para a venda
                transaction = CashierTransaction(
                    cashier_id=active_cashier.id,
                    transaction_type='sale',
                    amount=final_price,  # Usar o preço final após desconto
                    description=f'Venda - {product.name} (Desconto: {discount_percentage}%)',
                    related_sale_id=sale.id
                )

                db.session.add(transaction)

            db.session.commit()

            flash('Venda registrada com sucesso!', 'success')
            return redirect(url_for('sales.list_sales'))

    return render_template('sales/form.html', products=products, form=form)