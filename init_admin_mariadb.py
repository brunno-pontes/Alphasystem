#!/usr/bin/env python3
"""
Script para inicializar o usuário administrador no banco de dados MariaDB
"""
import os
import sys
from dotenv import load_dotenv

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()

# Adiciona o diretório raiz ao path para importar outros módulos
sys.path.append(os.path.dirname(__file__))

def init_admin_user():
    """Inicializa o usuário administrador no banco de dados"""
    try:
        # Configuração do banco de dados
        print("Configurando conexão com o banco de dados...")
        
        # Importar dentro da função para garantir que as variáveis de ambiente sejam carregadas
        from app import create_app
        from app.models import db, User
        from werkzeug.security import generate_password_hash
        
        # Criar aplicação
        app = create_app()
        
        with app.app_context():
            # Criar tabelas se não existirem
            print("Criando tabelas no banco de dados...")
            db.create_all()
            
            # Verificar se o usuário administrador já existe
            admin_user = User.query.filter_by(username='admin').first()
            
            if not admin_user:
                # Criar usuário administrador
                admin = User(
                    username='admin',
                    email='admin@alpha.com',
                    password=generate_password_hash('admin123'),
                    is_admin=True
                )
                
                db.session.add(admin)
                db.session.commit()
                
                print("Usuário administrador criado com sucesso!")
                print("Username: admin")
                print("Senha padrão: admin123")
                print("Email: admin@alpha.com")
            else:
                print("Usuário administrador já existe.")
                
    except Exception as e:
        print(f"Erro ao inicializar o usuário administrador: {e}")
        # Log do erro mais detalhado
        import traceback
        traceback.print_exc()
        return False
    
    print("Usuário administrador inicializado com sucesso.")
    return True


if __name__ == "__main__":
    print("Iniciando script de inicialização do administrador...")
    init_admin_user()