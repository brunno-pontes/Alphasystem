from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from flask_login import login_user
from app.models import User
from app import db
from app.utils.license_manager import license_manager
from werkzeug.security import generate_password_hash, check_password_hash

bp = Blueprint('auth', __name__)

@bp.route('/login', methods=['GET', 'POST'])
def login():
    # A tela de login não precisa de licença válida
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password, password):
            # Verificar licença específica do usuário após login, exceto para administradores
            if not user.is_admin:
                # Para usuários normais, verificar se têm uma licença válida associada
                if not user.license_key:
                    flash('Usuário não tem licença associada. Contate o administrador.', 'error')
                    return redirect(url_for('auth.login'))

                # Verificar se a licença do usuário é válida
                from app.models import License
                user_license = License.query.filter_by(license_key=user.license_key).first()
                if not user_license or not user_license.is_valid():
                    flash('Licença inválida ou expirada. Contate o administrador.', 'error')
                    return redirect(url_for('auth.login'))

            # Usar login_user do Flask-Login para autenticar o usuário
            login_user(user)
            # Redirecionar com base no tipo de usuário
            if user.role == 'user' and not user.is_admin:  # Usuário comum
                return redirect(url_for('products.list_products'))
            else:  # Gerente ou admin
                return redirect(url_for('main.dashboard'))
        else:
            flash('Credenciais inválidas', 'error')

    return render_template('auth/login.html')

@bp.route('/logout')
def logout():
    from flask_login import logout_user
    logout_user()
    return redirect(url_for('auth.login'))