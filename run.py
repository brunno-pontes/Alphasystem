from app import create_app, db
from app.models import User, Product, Sale, License, Cashier, CashierTransaction
from app.utils.license_manager import license_manager
from app.utils.logger import setup_logger
import os

app = create_app()

# Configurar logging
setup_logger(app)

# Criar tabelas no banco de dados
try:
    with app.app_context():
        # Criar todas as tabelas no banco de dados
        db.create_all()
        # Iniciar validação de licença em background
        # license_manager.setup_background_validation()
        app.logger.info("Aplicação iniciada com sucesso!")
        print("Aplicação iniciada com sucesso!")
except Exception as e:
    print(f"Erro ao tentar conectar ao banco de dados: {e}")
    print("Verifique as configurações do banco de dados no arquivo .env")
    app.logger.error(f"Erro ao tentar conectar ao banco de dados: {e}")

if __name__ == '__main__':
    app.run(debug=True, port=5007)