import os
from dotenv import load_dotenv

# Carregar variáveis de ambiente do arquivo .env ANTES de importar outros módulos
load_dotenv()

from app import create_app, db
from app.models import User, Product, Sale, License, Cashier, CashierTransaction
from app.utils.license_manager import license_manager
from app.utils.logger import setup_logger

app = create_app()

# Configurar logging
setup_logger(app)

# Criar tabelas no banco de dados local
try:
    with app.app_context():
        # Criar todas as tabelas no banco de dados local
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
            print('Banco de dados local atualizado com sucesso!')
        except Exception as migration_error:
            print(f'Erro durante a atualização do banco de dados local: {migration_error}')
            db.session.rollback()

        # Iniciar validação de licença em background
        # license_manager.setup_background_validation()
        app.logger.info("Aplicação iniciada com sucesso!")
        print("Aplicação iniciada com sucesso!")
except Exception as e:
    print(f"Erro ao tentar conectar ao banco de dados local: {e}")
    print("Verifique as configurações do banco de dados local no arquivo .env")
    app.logger.error(f"Erro ao tentar conectar ao banco de dados local: {e}")

if __name__ == '__main__':
    app.run(debug=True, port=5007)