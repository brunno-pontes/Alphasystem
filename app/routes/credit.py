from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required
from app import db
from app.models import CustomerCredit, ConsumptionRecord
from datetime import datetime

bp = Blueprint('credit', __name__, url_prefix='/credit')

@bp.route('/customers')
@login_required
def list_customers():
    """Lista todos os clientes fiado"""
    customers = CustomerCredit.query.all()
    return render_template('credit/customers.html', customers=customers)

@bp.route('/customers/new', methods=['GET', 'POST'])
@login_required
def add_customer():
    """Cadastrar novo cliente fiado"""
    if request.method == 'POST':
        name = request.form.get('name')
        phone = request.form.get('phone')

        # Validar campos
        if not name:
            flash('Nome do cliente é obrigatório!', 'error')
            return render_template('credit/add_customer.html')

        # Criar novo cliente
        customer = CustomerCredit(name=name, phone=phone)
        db.session.add(customer)
        db.session.commit()

        flash(f'Cliente {name} cadastrado com sucesso!', 'success')
        return redirect(url_for('credit.list_customers'))

    return render_template('credit/add_customer.html')

@bp.route('/customers/<int:customer_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_customer(customer_id):
    """Editar cliente fiado existente"""
    customer = CustomerCredit.query.get_or_404(customer_id)

    if request.method == 'POST':
        name = request.form.get('name')
        phone = request.form.get('phone')

        # Validar campos
        if not name:
            flash('Nome do cliente é obrigatório!', 'error')
            return render_template('credit/edit_customer.html', customer=customer)

        # Atualizar cliente
        customer.name = name
        customer.phone = phone

        db.session.commit()

        flash(f'Cliente {name} atualizado com sucesso!', 'success')
        return redirect(url_for('credit.list_customers'))

    return render_template('credit/edit_customer.html', customer=customer)

@bp.route('/customers/<int:customer_id>/delete', methods=['POST'])
@login_required
def delete_customer(customer_id):
    """Excluir cliente fiado"""
    customer = CustomerCredit.query.get_or_404(customer_id)

    # Verificar se o cliente tem registros de consumo pendentes
    pending_records = ConsumptionRecord.query.filter_by(customer_id=customer_id, paid=False).count()

    if pending_records > 0:
        flash(f'Não é possível excluir o cliente {customer.name} pois possui consumos pendentes!', 'error')
        return redirect(url_for('credit.list_customers'))

    customer_name = customer.name

    # Excluir primeiro os registros de consumo associados manualmente
    # Isso evita o erro de integridade quando SQLAlchemy tenta atualizar os registros antes de excluir
    consumption_records = ConsumptionRecord.query.filter_by(customer_id=customer_id).all()
    for record in consumption_records:
        db.session.delete(record)

    # Agora excluir o cliente
    db.session.delete(customer)
    db.session.commit()

    flash(f'Cliente {customer_name} excluído com sucesso!', 'success')
    return redirect(url_for('credit.list_customers'))

@bp.route('/consumption')
@login_required
def list_consumption():
    """Página para listar todos os itens de consumo"""
    # Obter o parâmetro de filtro (cliente_id) da query string
    customer_id_filter = request.args.get('customer_id', type=int)

    # Obter todos os clientes para o filtro
    all_customers = CustomerCredit.query.all()

    # Filtrar os registros de consumo com base no cliente selecionado
    if customer_id_filter:
        consumption_records = ConsumptionRecord.query.filter_by(customer_id=customer_id_filter).order_by(ConsumptionRecord.created_at.desc()).all()
        # Obter apenas o cliente específico
        selected_customer = CustomerCredit.query.get_or_404(customer_id_filter)
        filtered_customers = [selected_customer]
    else:
        consumption_records = ConsumptionRecord.query.order_by(ConsumptionRecord.created_at.desc()).all()
        filtered_customers = all_customers

    # Calcular totais gerais (apenas para os registros exibidos)
    total_consumed_general = 0.0
    total_paid_general = 0.0
    total_pending_general = 0.0

    # Vamos agrupar por cliente para facilitar a visualização
    records_by_customer = {}
    for record in consumption_records:
        if record.customer_id not in records_by_customer:
            records_by_customer[record.customer_id] = {
                'customer': record.customer,
                'records': [],
                'total_consumed': 0.0,
                'total_paid': 0.0,
                'total_pending': 0.0
            }

        records_by_customer[record.customer_id]['records'].append(record)

        # Calcular totais por cliente
        records_by_customer[record.customer_id]['total_consumed'] += record.total_value
        if record.paid:
            records_by_customer[record.customer_id]['total_paid'] += record.total_value
            total_paid_general += record.total_value
        else:
            records_by_customer[record.customer_id]['total_pending'] += record.total_value
            total_pending_general += record.total_value

        # Calcular totais gerais
        total_consumed_general += record.total_value

    return render_template('credit/consumption_list.html',
                          records_by_customer=records_by_customer,
                          consumption_records=consumption_records,
                          total_consumed_general=total_consumed_general,
                          total_paid_general=total_paid_general,
                          total_pending_general=total_pending_general,
                          all_customers=all_customers,
                          customer_id_filter=customer_id_filter)

@bp.route('/consumption/new')
@login_required
def register_consumption():
    """Página para registrar consumo de clientes fiado"""
    customers = CustomerCredit.query.all()
    return render_template('credit/register_consumption.html', customers=customers)

@bp.route('/consumption/add_item', methods=['POST'])
@login_required
def add_consumption_item():
    """Adiciona um item ao consumo do cliente"""
    data = request.get_json()

    customer_id = data.get('customer_id')
    item_description = data.get('item_description')
    item_price = data.get('item_price')

    if not customer_id or not item_description or not item_price:
        return jsonify({'error': 'Dados incompletos'}), 400

    customer = CustomerCredit.query.get_or_404(customer_id)

    # Aqui vamos armazenar o valor unitário para fins de cálculo futuro
    # Mas vamos criar um registro com o preço total (por enquanto apenas um item)
    record = ConsumptionRecord(
        customer_id=customer_id,
        item_description=item_description,
        total_value=float(item_price)
    )

    db.session.add(record)
    db.session.commit()

    # Recalcular a dívida total do cliente
    customer.calculate_total_debt()
    db.session.commit()

    return jsonify({
        'success': True,
        'total_debt': customer.total_debt,
        'record_id': record.id
    })

@bp.route('/consumption/<int:customer_id>/pay', methods=['POST'])
@login_required
def pay_consumption(customer_id):
    """Quita a dívida de um cliente"""
    customer = CustomerCredit.query.get_or_404(customer_id)

    # Marcar todos os registros pendentes como pagos
    pending_records = ConsumptionRecord.query.filter_by(customer_id=customer_id, paid=False).all()

    for record in pending_records:
        record.paid = True
        record.paid_date = datetime.now()

    db.session.commit()

    # Recalcular a dívida total (agora deve ser zero)
    customer.calculate_total_debt()
    db.session.commit()

    flash(f'Dívida do cliente {customer.name} quitada com sucesso!', 'success')
    return redirect(url_for('credit.register_consumption'))

@bp.route('/consumption/<int:record_id>/delete_item', methods=['POST'])
@login_required
def delete_consumption_item(record_id):
    """Remove um item do consumo do cliente"""
    record = ConsumptionRecord.query.get_or_404(record_id)
    
    db.session.delete(record)
    db.session.commit()
    
    # Recalcular a dívida total do cliente
    customer = record.customer
    customer.calculate_total_debt()
    db.session.commit()
    
    return jsonify({'success': True})