import os
from dotenv import load_dotenv

# Carregar variáveis de ambiente do arquivo .env ANTES de importar outros módulos
load_dotenv()

from app import create_app, db
from app.models import User, Product, Sale, License, Cashier, CashierTransaction, CustomerCredit, ConsumptionRecord
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

        # Verificar se as tabelas de crédito e consumo existem e criá-las se necessário
        try:
            # Verificar se a tabela customer_credit existe
            result = db.session.execute(text('''
                SELECT table_name
                FROM information_schema.tables
                WHERE table_schema = DATABASE()
                AND table_name = 'customer_credit'
            '''))

            if not result.fetchone():
                # Criar a tabela customer_credit
                db.session.execute(text('''
                    CREATE TABLE customer_credit (
                        id INTEGER PRIMARY KEY AUTO_INCREMENT,
                        name VARCHAR(150) NOT NULL,
                        phone VARCHAR(20),
                        total_debt FLOAT DEFAULT 0.0,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
                    )
                '''))
                print('Tabela customer_credit criada com sucesso.')

            # Verificar se a tabela consumption_record existe
            result = db.session.execute(text('''
                SELECT table_name
                FROM information_schema.tables
                WHERE table_schema = DATABASE()
                AND table_name = 'consumption_record'
            '''))

            if not result.fetchone():
                # Criar a tabela consumption_record
                db.session.execute(text('''
                    CREATE TABLE consumption_record (
                        id INTEGER PRIMARY KEY AUTO_INCREMENT,
                        customer_id INTEGER NOT NULL,
                        item_description VARCHAR(200) NOT NULL,
                        total_value FLOAT NOT NULL,
                        paid BOOLEAN DEFAULT FALSE,
                        paid_date DATETIME NULL,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                        FOREIGN KEY (customer_id) REFERENCES customer_credit(id)
                    )
                '''))
                print('Tabela consumption_record criada com sucesso.')
            else:
                # Verificar se a coluna item_description existe
                result = db.session.execute(text('''
                    SELECT column_name
                    FROM information_schema.columns
                    WHERE table_schema = DATABASE()
                    AND table_name = 'consumption_record'
                    AND column_name = 'item_description'
                '''))

                if not result.fetchone():
                    # Adicionar a coluna item_description
                    db.session.execute(text('ALTER TABLE consumption_record ADD COLUMN item_description VARCHAR(200) NOT NULL DEFAULT "Item não especificado"'))
                    print('Coluna item_description adicionada à tabela consumption_record.')

                    # Atualizar registros existentes para terem um valor padrão
                    db.session.execute(text('UPDATE consumption_record SET item_description = "Item não especificado" WHERE item_description IS NULL OR item_description = ""'))
                    print('Registros existentes atualizados com descrição padrão.')

            db.session.commit()
            print('Tabelas de crédito e consumo verificadas/atualizadas com sucesso!')
        except Exception as credit_migration_error:
            print(f'Erro durante a criação/atualização das tabelas de crédito e consumo: {credit_migration_error}')
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
    app.run(debug=True, host='0.0.0.0' ,port=5007)