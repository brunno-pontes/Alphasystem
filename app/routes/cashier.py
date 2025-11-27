from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import current_user, login_required
from app.models import Cashier, CashierTransaction, Sale
from app import db
from app.utils.decorators import license_required
from datetime import datetime

bp = Blueprint('cashier', __name__)

@bp.route('/cashier')
@license_required
def dashboard():
    """Dashboard do controle de caixa"""
    cashiers = Cashier.query.filter_by(user_id=current_user.id).order_by(Cashier.opening_date.desc()).all()
    active_cashier = Cashier.query.filter_by(user_id=current_user.id, status='open').first()
    
    return render_template('cashier/dashboard.html', cashiers=cashiers, active_cashier=active_cashier)

@bp.route('/cashier/open', methods=['GET', 'POST'])
@license_required
def open_cashier():
    """Abrir caixa"""
    if request.method == 'POST':
        try:
            initial_amount = float(request.form.get('initial_amount', 0))

            # Verificar se já existe um caixa aberto para este usuário
            existing_cashier = Cashier.query.filter_by(user_id=current_user.id, status='open').first()
            if existing_cashier:
                flash('Você já tem um caixa aberto!', 'error')
                return redirect(url_for('cashier.dashboard'))

            # Criar novo caixa
            cashier = Cashier(
                initial_amount=initial_amount,
                user_id=current_user.id,
                status='open'
            )

            db.session.add(cashier)
            db.session.commit()

            # Registrar transação de abertura
            transaction = CashierTransaction(
                cashier_id=cashier.id,
                transaction_type='entry',
                amount=initial_amount,
                description='Abertura de caixa'
            )
            db.session.add(transaction)
            db.session.commit()

            flash('Caixa aberto com sucesso!', 'success')
            return redirect(url_for('cashier.dashboard'))
        except ValueError:
            flash('Valor inicial inválido. Por favor, insira um número válido.', 'error')
            return render_template('cashier/open.html')
        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao abrir caixa: {str(e)}', 'error')
            return render_template('cashier/open.html')

    return render_template('cashier/open.html')

@bp.route('/cashier/close/<int:cashier_id>', methods=['POST'])
@license_required
def close_cashier(cashier_id):
    """Fechar caixa"""
    cashier = Cashier.query.filter_by(id=cashier_id, user_id=current_user.id).first_or_404()
    
    if cashier.status != 'open':
        flash('Este caixa já está fechado!', 'error')
        return redirect(url_for('cashier.dashboard'))
    
    # Calcular total de vendas e saldo final
    total_sales = cashier.calculate_total_sales()
    balance = cashier.calculate_balance()
    
    cashier.closing_date = datetime.utcnow()
    cashier.total_sales = total_sales
    cashier.final_amount = balance
    cashier.status = 'closed'
    
    db.session.commit()
    
    flash(f'Caixa fechado com sucesso! Saldo final: R$ {balance:.2f}', 'success')
    return redirect(url_for('cashier.dashboard'))

@bp.route('/cashier/expenses', methods=['GET', 'POST'])
@license_required
def expenses():
    """Registro de despesas"""
    active_cashier = Cashier.query.filter_by(user_id=current_user.id, status='open').first()
    
    if not active_cashier:
        flash('Você precisa abrir o caixa primeiro!', 'error')
        return redirect(url_for('cashier.dashboard'))
    
    if request.method == 'POST':
        amount = float(request.form.get('amount'))
        description = request.form.get('description')
        
        if amount <= 0:
            flash('O valor da despesa deve ser maior que zero!', 'error')
            return render_template('cashier/expenses.html', active_cashier=active_cashier)
        
        # Registrar despesa
        transaction = CashierTransaction(
            cashier_id=active_cashier.id,
            transaction_type='expense',
            amount=amount,
            description=description
        )
        
        db.session.add(transaction)
        active_cashier.total_expenses += amount
        db.session.commit()
        
        flash('Despesa registrada com sucesso!', 'success')
        return redirect(url_for('cashier.expenses'))
    
    expenses = CashierTransaction.query.filter_by(
        cashier_id=active_cashier.id,
        transaction_type='expense'
    ).order_by(CashierTransaction.transaction_date.desc()).all()
    
    return render_template('cashier/expenses.html', 
                         active_cashier=active_cashier, 
                         expenses=expenses)

@bp.route('/cashier/transactions')
@license_required
def transactions():
    """Listar todas as transações do caixa ativo"""
    active_cashier = Cashier.query.filter_by(user_id=current_user.id, status='open').first()
    
    if not active_cashier:
        flash('Você precisa abrir o caixa primeiro!', 'error')
        return redirect(url_for('cashier.dashboard'))
    
    transactions = CashierTransaction.query.filter_by(
        cashier_id=active_cashier.id
    ).order_by(CashierTransaction.transaction_date.desc()).all()
    
    return render_template('cashier/transactions.html',
                         active_cashier=active_cashier,
                         transactions=transactions)

@bp.route('/cashier/history')
@license_required
def history():
    """Histórico de caixas"""
    cashiers = Cashier.query.filter_by(user_id=current_user.id).order_by(Cashier.opening_date.desc()).all()
    return render_template('cashier/history.html', cashiers=cashiers)

@bp.route('/cashier/api/sales_for_cashier/<int:cashier_id>')
@login_required
def api_sales_for_cashier(cashier_id):
    """API para obter vendas associadas a um caixa"""
    cashier = Cashier.query.filter_by(id=cashier_id, user_id=current_user.id).first_or_404()

    # Obter vendas associadas diretamente ao caixa
    sales = Sale.query.filter_by(cashier_id=cashier.id).order_by(Sale.sale_date.desc()).all()

    sales_data = []
    for sale in sales:
        sales_data.append({
            'id': sale.id,
            'product_name': sale.product.name,
            'quantity': sale.quantity,
            'total_price': sale.total_price,
            'sale_date': sale.sale_date.strftime('%d/%m/%Y %H:%M') if sale.sale_date else ''
        })

    return jsonify(sales_data)