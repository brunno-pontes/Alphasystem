from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from app.models import License, User
from app import db
from app.utils.license_manager import license_manager
from datetime import datetime, timedelta
from functools import wraps
from flask_wtf import FlaskForm
from wtforms import StringField, EmailField, IntegerField, SelectField
from wtforms.validators import DataRequired, Email
import os

bp = Blueprint('licenses', __name__)

class LicenseForm(FlaskForm):
    class Meta:
        csrf = True
        csrf_secret = os.environ.get('SECRET_KEY', 'sua_chave_secreta_aqui').encode('utf-8')

def admin_required(f):
    """
    Decorator para verificar se o usuário é administrador
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        from flask_login import current_user
        from flask import session

        # Primeiro verificar com Flask-Login
        if not current_user.is_authenticated:
            flash('Faça login para acessar esta página.', 'error')
            return redirect(url_for('auth.login'))

        # Verificar se é admin usando o objeto current_user do Flask-Login
        if not current_user.is_admin:
            flash('Acesso negado. Apenas administradores podem acessar esta página.', 'error')
            return redirect(url_for('main.dashboard'))

        return f(*args, **kwargs)
    return decorated_function

@bp.route('/licenses')
@admin_required
def list_licenses():
    """
    Lista todas as licenças com opções de filtragem
    """
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '')
    status_filter = request.args.get('status', '')  # 'active', 'expired', 'inactive'
    
    licenses_query = License.query
    
    # Aplicar busca
    if search:
        licenses_query = licenses_query.filter(
            db.or_(
                License.client_name.contains(search),
                License.client_email.contains(search),
                License.license_key.contains(search)
            )
        )
    
    # Aplicar filtro de status
    if status_filter == 'active':
        licenses_query = licenses_query.filter(
            License.is_active == True,
            License.expiry_date > datetime.utcnow()
        )
    elif status_filter == 'expired':
        licenses_query = licenses_query.filter(
            License.expiry_date < datetime.utcnow()
        )
    elif status_filter == 'inactive':
        licenses_query = licenses_query.filter(License.is_active == False)
    
    licenses = licenses_query.order_by(License.created_at.desc()).paginate(
        page=page, per_page=10, error_out=False
    )
    
    return render_template('licenses/list.html', licenses=licenses, search=search, status_filter=status_filter)

@bp.route('/licenses/new', methods=['GET', 'POST'])
@admin_required
def create_license():
    """
    Cria uma nova licença para um cliente
    """
    form = LicenseForm()

    if request.method == 'POST' and form.validate_on_submit():
        client_name = request.form.get('client_name')
        client_email = request.form.get('client_email')
        days_valid = request.form.get('days_valid', type=int)
        user_type = request.form.get('user_type', 'user')  # 'user' ou 'manager'

        if not client_name or not client_email or not days_valid:
            flash('Preencha todos os campos obrigatórios.', 'error')
            return render_template('licenses/form.html', form=form)

        # Criar nova licença
        license = License(
            client_name=client_name,
            client_email=client_email,
            expiry_date=datetime.utcnow() + timedelta(days=days_valid),
            user_type=user_type
        )

        # Gerar chave de licença
        license.license_key = license.generate_license_key()

        db.session.add(license)
        db.session.commit()

        # Para ambiente local: tentar salvar também no banco online para validação
        try:
            license_data = {
                'license_key': license.license_key,
                'client_name': license.client_name,
                'client_email': license.client_email,
                'expiry_date': license.expiry_date,
                'is_active': license.is_active,
                'user_type': license.user_type,
                'created_at': license.created_at,
                'last_validation': license.last_validation
            }

            # Salvar no banco online para que outras instâncias possam validar
            result = License.save_license_online(license_data)
            if result['success']:
                flash('Licença criada e registrada no servidor online com sucesso!', 'success')
            else:
                flash(f'Licença criada localmente, mas não foi registrada no servidor online: {result["message"]}', 'warning')
        except Exception as e:
            flash(f'Licença criada localmente, mas ocorreu um erro ao registrar no servidor online: {str(e)}', 'warning')

        flash(f'Licença criada com sucesso! Chave: {license.license_key}', 'success')
        return redirect(url_for('licenses.list_licenses'))

    return render_template('licenses/form.html', form=form)

@bp.route('/licenses/edit/<int:id>', methods=['GET', 'POST'])
@admin_required
def edit_license(id):
    """
    Edita uma licença existente
    """
    license = License.query.get_or_404(id)
    form = LicenseForm()

    if request.method == 'POST' and form.validate_on_submit():
        client_name = request.form.get('client_name')
        client_email = request.form.get('client_email')
        expiry_date_str = request.form.get('expiry_date')
        is_active = request.form.get('is_active') == 'on'
        user_type = request.form.get('user_type', 'user')

        if not client_name or not client_email or not expiry_date_str:
            flash('Preencha todos os campos obrigatórios.', 'error')
            return render_template('licenses/form.html', license=license, form=form)

        # Converter a data
        try:
            expiry_date = datetime.strptime(expiry_date_str, '%Y-%m-%d')
        except ValueError:
            flash('Formato de data inválido.', 'error')
            return render_template('licenses/form.html', license=license, form=form)

        license.client_name = client_name
        license.client_email = client_email
        license.expiry_date = expiry_date
        license.is_active = is_active
        license.user_type = user_type

        db.session.commit()

        flash('Licença atualizada com sucesso!', 'success')
        return redirect(url_for('licenses.list_licenses'))

    return render_template('licenses/form.html', license=license, form=form)

@bp.route('/licenses/delete/<int:id>', methods=['POST'])
@admin_required
def delete_license(id):
    """
    Exclui uma licença
    """
    license = License.query.get_or_404(id)
    
    db.session.delete(license)
    db.session.commit()
    
    flash('Licença excluída com sucesso!', 'success')
    return redirect(url_for('licenses.list_licenses'))

@bp.route('/licenses/<int:id>/toggle', methods=['POST'])
@admin_required
def toggle_license(id):
    """
    Ativa/desativa uma licença
    """
    license = License.query.get_or_404(id)
    license.is_active = not license.is_active
    db.session.commit()
    
    status = 'ativada' if license.is_active else 'desativada'
    flash(f'Licença {status} com sucesso!', 'success')
    return jsonify({'success': True, 'is_active': license.is_active})

@bp.route('/licenses/<int:id>/details')
@admin_required
def license_details(id):
    """
    Mostra detalhes de uma licença específica
    """
    license = License.query.get_or_404(id)
    return render_template('licenses/details.html', license=license)

@bp.route('/licenses/generate_key', methods=['POST'])
@admin_required
def generate_license_key():
    """
    Gera uma nova chave de licença (sem salvar no banco)
    """
    client_name = request.form.get('client_name', 'Cliente')
    client_email = request.form.get('client_email', 'cliente@exemplo.com')
    
    # Criar uma instância temporária para gerar a chave
    temp_license = License(
        client_name=client_name,
        client_email=client_email,
        expiry_date=datetime.utcnow() + timedelta(days=30)
    )
    
    new_key = temp_license.generate_license_key()
    return jsonify({'key': new_key})