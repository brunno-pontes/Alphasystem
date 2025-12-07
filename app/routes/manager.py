from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import current_user
from app.models import User, License, Cashier, Sale, Product
from app import db
from sqlalchemy import func
from app.utils.license_manager import check_license
from werkzeug.security import generate_password_hash
from functools import wraps
from datetime import datetime
from flask_wtf import FlaskForm
import os


class ManagerForm(FlaskForm):
    class Meta:
        csrf = True
        csrf_secret = os.environ.get('SECRET_KEY', 'sua_chave_secreta_aqui').encode('utf-8')

bp = Blueprint('manager', __name__)

def manager_required(f):
    """
    Decorator para verificar se o usuário é um gerente
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Você precisa estar logado para acessar esta página.', 'error')
            return redirect(url_for('auth.login'))
        
        if current_user.role != 'manager' and not current_user.is_admin:
            flash('Acesso negado. Apenas gerentes podem acessar esta página.', 'error')
            return redirect(url_for('main.dashboard'))
        
        return f(*args, **kwargs)
    return decorated_function

@bp.route('/manager')
@manager_required
def index():
    """Página principal do painel do gerente"""
    managed_users = User.query.filter_by(manager_id=current_user.id).all()
    total_managed_users = len(managed_users)

    # Obter caixas abertos dos usuários gerenciados
    managed_users_ids = [user.id for user in managed_users]
    open_cashiers = Cashier.query.filter(
        Cashier.user_id.in_(managed_users_ids),
        Cashier.status == 'open'
    ).all()

    # Obter vendas do dia dos usuários gerenciados
    today = datetime.utcnow().date()
    today_sales = []
    total_daily_sales = 0
    total_daily_revenue = 0

    if managed_users_ids:  # Apenas executar a query se houver usuários gerenciados
        today_sales = db.session.query(Sale).join(Cashier, Sale.cashier_id == Cashier.id).join(User, Cashier.user_id == User.id).filter(
            Sale.sale_date >= datetime(today.year, today.month, today.day),
            Sale.sale_date < datetime(today.year, today.month, today.day + 1),
            User.id.in_(managed_users_ids)
        ).all()

        # Calcular resumo das vendas do dia
        total_daily_sales = len(today_sales)
        total_daily_revenue = sum(sale.total_price for sale in today_sales)

    # Obter as últimas vendas
    recent_sales = []
    if managed_users_ids:  # Apenas executar a query se houver usuários gerenciados
        recent_sales = db.session.query(Sale).join(Cashier, Sale.cashier_id == Cashier.id).join(User, Cashier.user_id == User.id).filter(
            User.id.in_(managed_users_ids)
        ).order_by(Sale.sale_date.desc()).limit(10).all()

    return render_template('manager/index.html',
                           managed_users=managed_users,
                           total_managed_users=total_managed_users,
                           open_cashiers=open_cashiers,
                           today_sales=today_sales,
                           total_daily_sales=total_daily_sales,
                           total_daily_revenue=total_daily_revenue,
                           recent_sales=recent_sales)

@bp.route('/manager/users')
@manager_required
def list_users():
    """Listar usuários gerenciados"""
    managed_users = User.query.filter_by(manager_id=current_user.id).all()
    return render_template('manager/users.html', managed_users=managed_users)

@bp.route('/manager/users/new', methods=['GET', 'POST'])
@manager_required
def new_user():
    """Criar novo usuário"""
    form = ManagerForm()

    if request.method == 'POST' and form.validate_on_submit():
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        license_key = request.form.get('license_key')  # Permite associar licença específica

        # Verificar se os campos obrigatórios estão preenchidos
        if not username or not email or not password:
            flash('Preencha todos os campos obrigatórios.', 'error')
            return render_template('manager/user_form.html', form=form)

        # Verificar se as senhas coincidem
        if password != confirm_password:
            flash('As senhas não coincidem.', 'error')
            return render_template('manager/user_form.html', form=form)

        # Verificar se o usuário ou email já existe
        existing_user = User.query.filter(
            (User.username == username) | (User.email == email)
        ).first()

        if existing_user:
            flash('Nome de usuário ou email já está em uso.', 'error')
            return render_template('manager/user_form.html', form=form)

        # Se for fornecida uma licença, verificar se ela existe e é válida
        assigned_license = None
        if license_key:
            from app.models import License
            assigned_license = License.query.filter_by(license_key=license_key).first()
            # Verificar se a licença pertence ao gerente (por meio de verificação de regras de negócio)
            # Por simplicidade, vamos permitir que gerentes usem suas próprias licenças ou licenças associadas a eles
            # Numa implementação completa, seria necessário ter um sistema de licenças alocadas ao gerente

        new_user = User(
            username=username,
            email=email,
            password=generate_password_hash(password),
            role='user',
            license_key=assigned_license.license_key if assigned_license else current_user.license_key,  # Usa licença fornecida ou herda do gerente
            manager_id=current_user.id
        )

        db.session.add(new_user)
        db.session.commit()

        flash('Usuário criado com sucesso!', 'success')
        return redirect(url_for('manager.list_users'))

    # Obter licenças disponíveis para o gerente (simplificação: mostrar todas as licenças do tipo 'user')
    from app.models import License
    # Filtrar apenas licenças do tipo 'user' que estejam ativas e válidas
    available_licenses = License.query.filter(
        License.user_type == 'user',
        License.is_active == True,
        License.expiry_date > func.now()
    ).all()

    return render_template('manager/user_form.html', available_licenses=available_licenses, form=form)

@bp.route('/manager/users/edit/<int:id>', methods=['GET', 'POST'])
@manager_required
def edit_user(id):
    """Editar usuário gerenciado"""
    form = ManagerForm()
    user = User.query.filter_by(id=id, manager_id=current_user.id).first_or_404()

    if request.method == 'POST' and form.validate_on_submit():
        username = request.form.get('username')
        email = request.form.get('email')
        new_password = request.form.get('password')

        # Verificar se o usuário ou email já está sendo usado por outro usuário
        existing_user = User.query.filter(
            ((User.username == username) | (User.email == email)) & (User.id != id)
        ).first()

        if existing_user:
            flash('Nome de usuário ou email já está em uso por outro usuário.', 'error')
            return render_template('manager/user_form.html', user=user, form=form)

        # Atualizar os dados do usuário
        user.username = username
        user.email = email

        # Atualizar a senha se foi fornecida
        if new_password:
            user.password = generate_password_hash(new_password)

        db.session.commit()

        flash('Usuário atualizado com sucesso!', 'success')
        return redirect(url_for('manager.list_users'))

    return render_template('manager/user_form.html', user=user, form=form)

@bp.route('/manager/users/delete/<int:id>', methods=['POST'])
@manager_required
def delete_user(id):
    """Excluir usuário gerenciado"""
    user = User.query.filter_by(id=id, manager_id=current_user.id).first_or_404()
    
    # Não permitir excluir o próprio gerente
    if user.id == current_user.id:
        flash('Você não pode excluir sua própria conta.', 'error')
        return redirect(url_for('manager.list_users'))
    
    db.session.delete(user)
    db.session.commit()
    
    flash('Usuário excluído com sucesso!', 'success')
    return redirect(url_for('manager.list_users'))