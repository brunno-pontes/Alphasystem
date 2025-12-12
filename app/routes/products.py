from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from app.models import Product
from app import db
from app.utils.decorators import license_required
from decimal import Decimal
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, FloatField, IntegerField
from wtforms.validators import DataRequired
import os


class ProductForm(FlaskForm):
    class Meta:
        csrf = True
        csrf_secret = os.environ.get('SECRET_KEY', 'sua_chave_secreta_aqui').encode('utf-8')

bp = Blueprint('products', __name__)

def validate_positive_number(value, field_name):
    """Valida se um valor é um número positivo"""
    try:
        number = Decimal(str(value))
        if number < 0:
            raise ValueError(f'{field_name} deve ser um número positivo.')
        return number
    except:
        raise ValueError(f'{field_name} deve ser um número válido.')

def validate_non_empty_string(value, field_name):
    """Valida se uma string não está vazia"""
    if not value or not value.strip():
        raise ValueError(f'{field_name} é obrigatório.')
    return value.strip()

@bp.route('/products')
@license_required
def list_products():
    from flask_wtf import FlaskForm
    form = FlaskForm()
    query = request.args.get('q', '')
    if query:
        products = Product.query.filter(Product.name.ilike(f'%{query}%')).all()
    else:
        products = Product.query.all()
    return render_template('products/list.html', products=products, query=query, form=form)

@bp.route('/products/new', methods=['GET', 'POST'])
@license_required
def new_product():
    form = ProductForm()

    if request.method == 'POST' and form.validate_on_submit():
        try:
            name = validate_non_empty_string(request.form.get('name'), 'Nome')
            description = request.form.get('description', '').strip()
            price = float(validate_positive_number(request.form.get('price'), 'Preço'))
            quantity = int(validate_positive_number(request.form.get('quantity'), 'Quantidade'))
            category = request.form.get('category', '').strip()

            product = Product(
                name=name,
                description=description,
                price=price,
                quantity=quantity,
                category=category
            )

            # Validar dados do produto
            validation_errors = product.validate_data()
            if validation_errors:
                for error in validation_errors:
                    flash(error, 'error')
                return render_template('products/form.html', form=form)

            db.session.add(product)
            db.session.commit()

            # Atualizar o estoque máximo após criar o produto
            product.update_max_quantity()
            db.session.commit()

            flash('Produto adicionado com sucesso!', 'success')
            return redirect(url_for('products.list_products'))
        except ValueError as e:
            flash(str(e), 'error')
        except Exception as e:
            flash('Erro ao adicionar produto: {}'.format(str(e)), 'error')

    return render_template('products/form.html', form=form)

@bp.route('/products/edit/<int:id>', methods=['GET', 'POST'])
@license_required
def edit_product(id):
    product = Product.query.get_or_404(id)
    form = ProductForm()

    if request.method == 'POST' and form.validate_on_submit():
        try:
            product.name = validate_non_empty_string(request.form.get('name'), 'Nome')
            product.description = request.form.get('description', '').strip()
            product.price = float(validate_positive_number(request.form.get('price'), 'Preço'))
            product.quantity = int(validate_positive_number(request.form.get('quantity'), 'Quantidade'))
            product.category = request.form.get('category', '').strip()

            # Validar dados do produto
            validation_errors = product.validate_data()
            if validation_errors:
                for error in validation_errors:
                    flash(error, 'error')
                return render_template('products/form.html', product=product, form=form)

            # Atualizar o estoque máximo após atualizar o produto
            product.update_max_quantity()
            db.session.commit()

            flash('Produto atualizado com sucesso!', 'success')
            return redirect(url_for('products.list_products'))
        except ValueError as e:
            flash(str(e), 'error')
        except Exception as e:
            flash('Erro ao atualizar produto: {}'.format(str(e)), 'error')

    return render_template('products/form.html', product=product, form=form)

@bp.route('/products/delete/<int:id>', methods=['POST'])
@license_required
def delete_product(id):
    product = Product.query.get_or_404(id)

    # Primeiro deletar todas as vendas associadas ao produto manualmente
    # para evitar o problema de atualização do product_id para NULL
    from app.models import Sale
    sales_to_delete = Sale.query.filter_by(product_id=id).all()
    for sale in sales_to_delete:
        db.session.delete(sale)

    # Depois deletar o produto
    db.session.delete(product)
    db.session.commit()

    flash('Produto excluído com sucesso!', 'success')
    return redirect(url_for('products.list_products'))