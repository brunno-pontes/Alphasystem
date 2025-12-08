#!/usr/bin/env python3
"""
Script para verificar licenças no banco online
"""
import os
import sys
from dotenv import load_dotenv
load_dotenv()

def check_online_licenses():
    """Verifica as licenças existentes no banco online"""
    try:
        from app import create_app
        from app.database_manager import database_manager
        from sqlalchemy import text
        
        app = create_app()
        
        with app.app_context():
            # Conectar ao banco online
            online_session = database_manager.get_online_db_session()
            
            # Contar licenças existentes
            count_result = online_session.execute(text("SELECT COUNT(*) FROM license")).fetchone()
            total_licenses = count_result[0]
            
            print(f"Total de licenças no banco online (alpha_licenca): {total_licenses}")
            
            if total_licenses > 0:
                # Listar licenças
                licenses = online_session.execute(text("SELECT license_key, client_name, client_email, expiry_date, is_active FROM license")).fetchall()
                
                print("\nLicenças no banco online:")
                print("-" * 80)
                for license in licenses:
                    status = "ATIVA" if license.is_active and license.expiry_date > app.config['db'].func.now() else "INATIVA"
                    print(f"Chave: {license.license_key}")
                    print(f"Cliente: {license.client_name} <{license.client_email}>")
                    print(f"Expira em: {license.expiry_date}")
                    print(f"Status: {status}")
                    print("-" * 80)
            else:
                print("Nenhuma licença encontrada no banco online.")
            
            online_session.close()
            
    except Exception as e:
        print(f"Erro ao verificar licenças no banco online: {e}")
        import traceback
        traceback.print_exc()

def check_local_licenses():
    """Verifica as licenças existentes no banco local"""
    try:
        from app import create_app
        from app.models import License
        from datetime import datetime

        app = create_app()

        with app.app_context():
            # Obter licenças do banco local
            licenses = License.query.all()
            print(f"\nTotal de licenças no banco local (alpha_local): {len(licenses)}")

            if licenses:
                print("\nLicenças no banco local:")
                print("-" * 80)
                for license in licenses:
                    status = "ATIVA" if license.is_active and license.expiry_date > datetime.utcnow() else "INATIVA"
                    print(f"Chave: {license.license_key}")
                    print(f"Cliente: {license.client_name} <{license.client_email}>")
                    print(f"Expira em: {license.expiry_date}")
                    print(f"Status: {status}")
                    print("-" * 80)
            else:
                print("Nenhuma licença encontrada no banco local.")

    except Exception as e:
        print(f"Erro ao verificar licenças no banco local: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("=== Verificação de Licenças ===")
    check_local_licenses()
    check_online_licenses()