from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from flask_login import login_user
from app.models import User
from app import db
from app.utils.license_manager import license_manager
from app.utils.password_utils import validate_password_strength
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import URLSafeTimedSerializer
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.csrf.session import SessionCSRF
from datetime import timedelta


class LoginForm(FlaskForm):
    class Meta:
        csrf = True
        csrf_secret = os.environ.get('SECRET_KEY', 'sua_chave_secreta_aqui').encode('utf-8')

# Configurações de email
EMAIL_HOST = os.environ.get('EMAIL_HOST', 'smtp.gmail.com')
EMAIL_PORT = int(os.environ.get('EMAIL_PORT', 587))
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD')

bp = Blueprint('auth', __name__)
serializer = URLSafeTimedSerializer(os.environ.get('SECRET_KEY', 'sua_chave_secreta_aqui'))

def send_reset_email(email, token):
    """Envia email de recuperação de senha"""
    msg = MIMEMultipart()
    msg['Subject'] = 'Recuperação de Senha - Alphasystem'
    msg['From'] = EMAIL_HOST_USER
    msg['To'] = email

    reset_url = url_for('auth.reset_with_token', token=token, _external=True)
    body = f"""
    Você solicitou a recuperação de senha para o Alphasystem.

    Clique no link abaixo para redefinir sua senha:
    {reset_url}

    Se não foi você quem solicitou a recuperação, ignore este email.
    """

    msg.attach(MIMEText(body, 'plain'))

    try:
        server = smtplib.SMTP(EMAIL_HOST, EMAIL_PORT)
        server.starttls()
        server.login(EMAIL_HOST_USER, EMAIL_HOST_PASSWORD)
        server.send_message(msg)
        server.quit()
        return True
    except:
        return False

@bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()

    # A tela de login não precisa de licença válida
    if request.method == 'POST' and form.validate_on_submit():
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

    return render_template('auth/login.html', form=form)

@bp.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    form = LoginForm()

    if request.method == 'POST' and form.validate_on_submit():
        email = request.form.get('email')

        if not email:
            flash('Por favor, informe seu email.', 'error')
            return render_template('auth/forgot_password.html', form=form)

        user = User.query.filter_by(email=email).first()

        if user:
            token = serializer.dumps(email, salt='password-reset-salt')

            if send_reset_email(email, token):
                flash('Email de recuperação enviado. Verifique sua caixa de entrada.', 'info')
            else:
                flash('Erro ao enviar email de recuperação. Tente novamente.', 'error')
        else:
            flash('Email não encontrado.', 'error')

    return render_template('auth/forgot_password.html', form=form)

@bp.route('/reset/<token>', methods=['GET', 'POST'])
def reset_with_token(token):
    form = LoginForm()
    try:
        email = serializer.loads(token, salt='password-reset-salt', max_age=3600)  # 1 hora
    except:
        flash('Token inválido ou expirado.', 'error')
        return redirect(url_for('auth.forgot_password'))

    if request.method == 'POST' and form.validate_on_submit():
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        if password != confirm_password:
            flash('Senhas não coincidem.', 'error')
            return render_template('auth/reset_password.html', token=token, form=form)

        is_valid, message = validate_password_strength(password)
        if not is_valid:
            flash(message, 'error')
            return render_template('auth/reset_password.html', token=token, form=form)

        user = User.query.filter_by(email=email).first()
        if user:
            user.password = generate_password_hash(password)
            db.session.commit()
            flash('Senha redefinida com sucesso. Faça login para continuar.', 'success')
            return redirect(url_for('auth.login'))
        else:
            flash('Usuário não encontrado.', 'error')

    return render_template('auth/reset_password.html', token=token, form=form)

@bp.route('/logout')
def logout():
    from flask_login import logout_user
    logout_user()
    return redirect(url_for('auth.login'))