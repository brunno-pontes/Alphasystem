from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from app.models import Product
from app import db
from app.utils.decorators import license_required

bp = Blueprint('products', __name__)

@bp.route('/products')
@license_required
def list_products():
    products = Product.query.all()
    return render_template('products/list.html', products=products)

@bp.route('/products/new', methods=['GET', 'POST'])
@license_required
def new_product():
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        price = float(request.form.get('price'))
        quantity = int(request.form.get('quantity'))
        category = request.form.get('category')

        product = Product(
            name=name,
            description=description,
            price=price,
            quantity=quantity,
            category=category
        )

        db.session.add(product)
        db.session.commit()

        # Atualizar o estoque máximo após criar o produto
        product.update_max_quantity()
        db.session.commit()

        flash('Produto adicionado com sucesso!', 'success')
        return redirect(url_for('products.list_products'))

    return render_template('products/form.html')

@bp.route('/products/edit/<int:id>', methods=['GET', 'POST'])
@license_required
def edit_product(id):
    product = Product.query.get_or_404(id)

    if request.method == 'POST':
        product.name = request.form.get('name')
        product.description = request.form.get('description')
        product.price = float(request.form.get('price'))
        product.quantity = int(request.form.get('quantity'))
        product.category = request.form.get('category')

        # Atualizar o estoque máximo após atualizar o produto
        product.update_max_quantity()
        db.session.commit()

        flash('Produto atualizado com sucesso!', 'success')
        return redirect(url_for('products.list_products'))

    return render_template('products/form.html', product=product)

@bp.route('/products/delete/<int:id>', methods=['POST'])
@license_required
def delete_product(id):
    product = Product.query.get_or_404(id)
    db.session.delete(product)
    db.session.commit()

    flash('Produto excluído com sucesso!', 'success')
    return redirect(url_for('products.list_products'))