from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from app.models import User, License
from app import db
from werkzeug.security import generate_password_hash
from datetime import datetime
from flask_wtf import FlaskForm
import os


class RegistrationForm(FlaskForm):
    class Meta:
        csrf = True
        csrf_secret = os.environ.get('SECRET_KEY', 'sua_chave_secreta_aqui').encode('utf-8')

bp = Blueprint('registration', __name__)

@bp.route('/register_with_license', methods=['GET', 'POST'])
def register_with_license():
    """
    Rota para cadastro de usuário usando chave de licença
    """
    form = RegistrationForm()

    if request.method == 'POST' and form.validate_on_submit():
        license_key = request.form.get('license_key')
        username = request.form.get('username')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        # Validar campos
        if not license_key or not username or not password:
            flash('Preencha todos os campos obrigatórios.', 'error')
            return render_template('registration/register_with_license.html', form=form)

        if password != confirm_password:
            flash('As senhas não coincidem.', 'error')
            return render_template('registration/register_with_license.html', form=form)

        if len(password) < 6:
            flash('A senha deve ter pelo menos 6 caracteres.', 'error')
            return render_template('registration/register_with_license.html', form=form)

        # Verificar se a licença existe e é válida
        license = License.query.filter_by(license_key=license_key).first()

        if not license:
            flash('Chave de licença inválida.', 'error')
            return render_template('registration/register_with_license.html', form=form)

        if not license.is_valid():
            flash('A licença está expirada ou inválida.', 'error')
            return render_template('registration/register_with_license.html', form=form)

        # Verificar se já existe usuário com esse nome
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash('Nome de usuário já está em uso.', 'error')
            return render_template('registration/register_with_license.html', form=form)

        # Verificar se já existe usuário com o mesmo email da licença
        existing_email_user = User.query.filter_by(email=license.client_email).first()
        email_to_use = license.client_email  # Email padrão da licença

        if existing_email_user:
            # Se o email já está em uso, usar um email alternativo
            import re
            base_email = license.client_email
            local, domain = base_email.split('@')

            # Remover caracteres especiais e espaços do nome de usuário
            clean_username = re.sub(r'[^a-zA-Z0-9]', '', username.lower())

            # Usar o nome de usuário como base para o email
            email_to_use = f"{clean_username}@{domain}"

            # Garantir que o novo email não exista
            counter = 1
            original_email = email_to_use
            while User.query.filter_by(email=email_to_use).first():
                email_to_use = f"{clean_username}{counter}@{domain}"
                counter += 1

        # Criar novo usuário associado à licença
        new_user = User(
            username=username,
            email=email_to_use,  # Usar o email da licença (ou alternativo)
            password=generate_password_hash(password),
            role=license.user_type,  # Definir o role baseado no tipo de licença
            is_admin=False,  # Usuário normal
            license_key=license.license_key  # Associar a licença ao usuário
        )

        db.session.add(new_user)
        db.session.commit()

        flash('Conta criada com sucesso! Faça login para continuar.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('registration/register_with_license.html', form=form)