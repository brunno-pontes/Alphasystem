from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from app.models import User
from app import db
from app.utils.license_manager import license_manager
from werkzeug.security import check_password_hash

bp = Blueprint('debug', __name__)

@bp.route('/debug-login', methods=['POST'])
def debug_login():
    """Rota de debug para testar o login passo a passo"""
    username = request.form.get('username')
    password = request.form.get('password')
    
    print(f"Debug login - Usuário recebido: {username}")
    
    # Passo 1: Buscar usuário
    user = User.query.filter_by(username=username).first()
    
    if not user:
        print(f"Debug: Usuário '{username}' não encontrado")
        return {'success': False, 'message': f'Usuário {username} não encontrado'}
    
    print(f"Debug: Usuário encontrado - ID: {user.id}, Username: {user.username}, Admin: {user.is_admin}")
    
    # Passo 2: Verificar senha
    senha_correta = check_password_hash(user.password, password)
    print(f"Debug: Senha fornecida: {password}, Senha correta: {senha_correta}")
    
    if not senha_correta:
        print("Debug: Senha incorreta")
        return {'success': False, 'message': 'Senha incorreta'}
    
    # Passo 3: Criar sessão
    session['user_id'] = user.id
    print(f"Debug: Sessão criada para usuário {user.id}")
    
    # Passo 4: Verificar licença
    license_result = license_manager.check_license_status()
    print(f"Debug: Resultado da verificação de licença: {license_result}")
    
    # Para debug, não vamos aplicar a restrição de licença aqui
    return {
        'success': True,
        'user_id': user.id,
        'is_admin': user.is_admin,
        'license_valid': license_result['valid'],
        'license_message': license_result['message']
    }

# Adicionar rota para verificar sessão
@bp.route('/debug-session')
def debug_session():
    """Rota para verificar o status da sessão"""
    user_id = session.get('user_id')
    if user_id:
        user = User.query.get(user_id)
        return {
            'logged_in': True,
            'user_id': user_id,
            'username': user.username if user else 'Unknown',
            'is_admin': user.is_admin if user else False
        }
    else:
        return {'logged_in': False}