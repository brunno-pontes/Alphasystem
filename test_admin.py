#!/usr/bin/env python3
# Script para testar a verificação de permissões do admin
from app import create_app
from app.models import User

app = create_app()

with app.app_context():
    # Buscar o usuário admin
    admin = User.query.filter_by(username='admin').first()
    
    if admin:
        print(f"Usuário admin encontrado: {admin.username}")
        print(f"É admin? {admin.is_admin}")
        print(f"Tem hasattr is_admin? {hasattr(admin, 'is_admin')}")
        print(f"Role: {admin.role}")
        print(f"License Key: {admin.license_key}")
    else:
        print("Nenhum usuário admin encontrado")