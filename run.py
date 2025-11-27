from app import create_app, db
from app.models import User, Product, Sale, License, Cashier, CashierTransaction
from app.utils.license_manager import license_manager
import os

app = create_app()

# Criar tabelas no banco de dados
try:
    with app.app_context():
        # Criar todas as tabelas no banco de dados
        db.create_all()
        # Iniciar validação de licença em background
        # license_manager.setup_background_validation()
        print("Aplicação iniciada com sucesso!")
except Exception as e:
    print(f"Erro ao tentar conectar ao banco de dados: {e}")
    print("Verifique as configurações do banco de dados no arquivo .env")

if __name__ == '__main__':
    app.run(debug=True, port=5007)