#!/usr/bin/env python3
"""
Script para inicializar o usuário administrador no banco de dados MariaDB
"""
import os
import sys
from dotenv import load_dotenv

def init_admin_user():
    """Inicializa o usuário administrador no banco de dados"""
    try:
        # Carrega as variáveis de ambiente do arquivo .env ANTES de importar outros módulos
        load_dotenv()

        print(f"DATABASE_URL configurado: {os.environ.get('DATABASE_URL', 'Não definido')}")

        # Importar dentro da função para garantir que as variáveis de ambiente sejam carregadas
        from app import create_app
        from app.models import db, User
        from werkzeug.security import generate_password_hash

        # Criar aplicação
        app = create_app()

        with app.app_context():
            print(f"URI do banco de dados efetivo: {app.config.get('SQLALCHEMY_DATABASE_URI')}")

            # Criar tabelas se não existirem
            print("Criando tabelas no banco de dados...")
            db.create_all()

            # Atualizar estrutura do banco de dados para incluir colunas de desconto
            from sqlalchemy import text
            try:
                # Verificar se as colunas de desconto existem e adicioná-las se necessário
                result = db.session.execute(text('''
                    SELECT COLUMN_NAME
                    FROM information_schema.COLUMNS
                    WHERE TABLE_SCHEMA = DATABASE()
                    AND TABLE_NAME = 'sale'
                    AND COLUMN_NAME IN ('discount_percentage', 'discount_amount', 'final_price')
                '''))

                existing_columns = [row[0] for row in result.fetchall()]

                if 'discount_percentage' not in existing_columns:
                    db.session.execute(text('ALTER TABLE sale ADD COLUMN discount_percentage FLOAT DEFAULT 0.0'))
                    print('Coluna discount_percentage adicionada.')
                if 'discount_amount' not in existing_columns:
                    db.session.execute(text('ALTER TABLE sale ADD COLUMN discount_amount FLOAT DEFAULT 0.0'))
                    print('Coluna discount_amount adicionada.')
                if 'final_price' not in existing_columns:
                    db.session.execute(text('ALTER TABLE sale ADD COLUMN final_price FLOAT NOT NULL DEFAULT 0.0'))
                    print('Coluna final_price adicionada.')

                # Atualizar registros existentes para terem valores padrão para as novas colunas
                db.session.execute(text('''
                    UPDATE sale
                    SET discount_percentage = 0.0,
                        discount_amount = 0.0,
                        final_price = total_price
                    WHERE discount_percentage IS NULL OR discount_amount IS NULL OR final_price IS NULL
                '''))

                db.session.commit()
                print('Banco de dados atualizado com sucesso!')
            except Exception as migration_error:
                print(f'Erro durante a atualização do banco de dados: {migration_error}')
                db.session.rollback()

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