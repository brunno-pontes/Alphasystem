from flask_login import UserMixin
from app import db, login_manager
from datetime import datetime
import hashlib
import secrets

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(UserMixin, db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.Text, nullable=False)  # Usando Text para acomodar qualquer tamanho de hash
    is_admin = db.Column(db.Boolean, default=False)
    role = db.Column(db.String(50), default='user')  # 'admin', 'manager', 'user'
    license_key = db.Column(db.String(255), db.ForeignKey('license.license_key'), nullable=True)
    manager_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)  # Para usuários gerenciados por um gerente
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relacionamento com o gerente
    manager = db.relationship('User', remote_side=[id], backref='managed_users')

class Product(db.Model):
    __tablename__ = 'product'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    price = db.Column(db.Float, nullable=False)
    quantity = db.Column(db.Integer, default=0)
    max_quantity = db.Column(db.Integer, default=0)  # Quantidade máxima que o produto já teve
    category = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def update_max_quantity(self):
        """Atualiza a quantidade máxima se a quantidade atual for maior"""
        if self.quantity > self.max_quantity:
            self.max_quantity = self.quantity

    def validate_data(self):
        """Valida os dados do produto"""
        errors = []

        if not self.name or len(self.name.strip()) == 0:
            errors.append("Nome do produto é obrigatório")

        if self.price is None or self.price < 0:
            errors.append("Preço deve ser um número positivo")

        if self.quantity is None or self.quantity < 0:
            errors.append("Quantidade deve ser um número positivo")

        return errors

class Sale(db.Model):
    __tablename__ = 'sale'
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id', ondelete='CASCADE'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    total_price = db.Column(db.Float, nullable=False)
    discount_percentage = db.Column(db.Float, default=0.0)  # Percentual de desconto (0 a 100)
    discount_amount = db.Column(db.Float, default=0.0)  # Valor do desconto
    final_price = db.Column(db.Float, nullable=False, default=0.0)  # Preço final após desconto
    sale_date = db.Column(db.DateTime, default=datetime.utcnow)
    cashier_id = db.Column(db.Integer, db.ForeignKey('cashier.id'), nullable=True)  # Novo campo
    product = db.relationship('Product', backref='sales', passive_deletes=True)
    cashier = db.relationship('Cashier', backref='sales')  # Novo relacionamento


class Cashier(db.Model):
    """Modelo para controle de caixa"""
    __tablename__ = 'cashier'
    id = db.Column(db.Integer, primary_key=True)
    opening_date = db.Column(db.DateTime, default=datetime.utcnow)
    closing_date = db.Column(db.DateTime, nullable=True)
    initial_amount = db.Column(db.Float, default=0.0)
    final_amount = db.Column(db.Float, nullable=True)
    total_sales = db.Column(db.Float, default=0.0)
    total_expenses = db.Column(db.Float, default=0.0)
    status = db.Column(db.String(20), default='open')  # 'open', 'closed'
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', backref='cashiers')

    def calculate_total_sales(self):
        """Calcula o total de vendas para este caixa"""
        # Usar a associação direta com vendas ao invés de intervalo de datas
        sales = Sale.query.filter_by(cashier_id=self.id).all()
        self.total_sales = sum(sale.total_price for sale in sales)
        return self.total_sales

    def calculate_balance(self):
        """Calcula o saldo final do caixa"""
        return self.initial_amount + self.total_sales - self.total_expenses

    def calculate_current_balance(self):
        """Calcula o saldo atual do caixa (considerando transações registradas)"""
        # Obter todas as transações do caixa
        transactions = CashierTransaction.query.filter_by(cashier_id=self.id).all()

        balance = self.initial_amount
        for transaction in transactions:
            if transaction.transaction_type in ['sale', 'entry']:
                balance += transaction.amount
            elif transaction.transaction_type in ['expense', 'exit']:
                balance -= transaction.amount

        return balance


class CashierTransaction(db.Model):
    """Modelo para transações no caixa (vendas, despesas, etc.)"""
    __tablename__ = 'cashier_transaction'
    id = db.Column(db.Integer, primary_key=True)
    cashier_id = db.Column(db.Integer, db.ForeignKey('cashier.id'), nullable=False)
    transaction_type = db.Column(db.String(20), nullable=False)  # 'sale', 'expense', 'entry', 'exit'
    amount = db.Column(db.Float, nullable=False)
    description = db.Column(db.String(200))
    transaction_date = db.Column(db.DateTime, default=datetime.utcnow)
    related_sale_id = db.Column(db.Integer, db.ForeignKey('sale.id'), nullable=True)
    cashier = db.relationship('Cashier', backref='transactions')
    related_sale = db.relationship('Sale', backref='cashier_transactions')


class CustomerCredit(db.Model):
    """Modelo para clientes que compram fiado"""
    __tablename__ = 'customer_credit'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    phone = db.Column(db.String(20), nullable=True)
    total_debt = db.Column(db.Float, default=0.0)  # Dívida total acumulada
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<CustomerCredit {self.name}>'

    def calculate_total_debt(self):
        """Calcula a dívida total baseada nos registros de consumo"""
        total = 0
        for record in self.consumption_records:
            if not record.paid:
                total += record.total_value
        self.total_debt = total
        return total


class ConsumptionRecord(db.Model):
    """Modelo para registros de consumo de clientes fiado"""
    __tablename__ = 'consumption_record'
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer_credit.id'), nullable=False)
    item_description = db.Column(db.String(200), nullable=False)  # Descrição do item/produto
    total_value = db.Column(db.Float, nullable=False)  # Valor total da compra
    paid = db.Column(db.Boolean, default=False)  # Indica se a dívida foi quitada
    paid_date = db.Column(db.DateTime, nullable=True)  # Data em que a dívida foi quitada
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relacionamento com o cliente
    customer = db.relationship('CustomerCredit', backref='consumption_records')

    def __repr__(self):
        return f'<ConsumptionRecord {self.customer.name} - {self.item_description} - R${self.total_value:.2f}>'


class License(db.Model):
    __tablename__ = 'license'
    # Este modelo usará o banco de dados online para validação, mas pode ser armazenado localmente também
    id = db.Column(db.Integer, primary_key=True)
    license_key = db.Column(db.String(255), unique=True, nullable=False)
    client_name = db.Column(db.String(200), nullable=False)
    client_email = db.Column(db.String(200), nullable=False)
    expiry_date = db.Column(db.DateTime, nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    user_type = db.Column(db.String(20), default='user')  # 'user', 'manager'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_validation = db.Column(db.DateTime, default=datetime.utcnow)

    def generate_license_key(self):
        """Gera uma chave de licença única"""
        # Gerar uma chave baseada no nome do cliente e timestamp
        key_base = f"{self.client_name}{self.client_email}{self.created_at}{secrets.token_hex(8)}"
        return hashlib.sha256(key_base.encode()).hexdigest()[:32].upper()

    def is_valid(self):
        """Verifica se a licença está válida"""
        return self.is_active and self.expiry_date > datetime.utcnow()

    def needs_validation(self):
        """Verifica se a licença precisa ser validada (a cada 30 dias)"""
        if not self.last_validation:
            return True
        return (datetime.utcnow() - self.last_validation).days >= 30

    @classmethod
    def validate_license_online(cls, license_key):
        """
        Método de classe para validar uma licença diretamente no banco de dados online
        """
        from app.database_manager import database_manager
        from datetime import datetime
        from sqlalchemy import text

        try:
            online_session = database_manager.get_online_db_session()

            # Query direto no banco de dados online usando text()
            query = text("SELECT license_key, client_name, client_email, expiry_date, is_active FROM license WHERE license_key = :license_key")
            result = online_session.execute(query, {"license_key": license_key}).fetchone()

            if result:
                # Verificar se a licença está ativa e não expirada
                is_active = result.is_active
                expiry_date = result.expiry_date

                is_valid_online = is_active and expiry_date > datetime.utcnow()

                # Fechar a sessão
                online_session.close()

                return {
                    "valid": is_valid_online,
                    "license_data": {
                        "license_key": result.license_key,
                        "client_name": result.client_name,
                        "client_email": result.client_email,
                        "expiry_date": result.expiry_date,
                        "is_active": result.is_active
                    }
                }
            else:
                online_session.close()
                return {"valid": False, "license_data": None, "message": "Licença não encontrada no servidor online"}
        except Exception as e:
            try:
                online_session.close()
            except:
                pass
            return {"valid": False, "license_data": None, "message": f"Erro ao validar licença no servidor: {str(e)}"}

    @classmethod
    def save_license_online(cls, license_data):
        """
        Método de classe para salvar uma licença no banco de dados online
        Usado para registrar licenças válidas que serão usadas em outros clientes
        """
        from app.database_manager import database_manager
        from datetime import datetime
        from sqlalchemy import text

        try:
            online_session = database_manager.get_online_db_session()

            # Inserir a licença no banco de dados online
            query = text("""
                INSERT INTO license (license_key, client_name, client_email, expiry_date, is_active, user_type, created_at, last_validation)
                VALUES (:license_key, :client_name, :client_email, :expiry_date, :is_active, :user_type, :created_at, :last_validation)
            """)

            online_session.execute(query, {
                "license_key": license_data['license_key'],
                "client_name": license_data['client_name'],
                "client_email": license_data['client_email'],
                "expiry_date": license_data['expiry_date'],
                "is_active": license_data.get('is_active', True),
                "user_type": license_data.get('user_type', 'user'),
                "created_at": license_data.get('created_at', datetime.utcnow()),
                "last_validation": license_data.get('last_validation', datetime.utcnow())
            })

            online_session.commit()
            online_session.close()

            return {"success": True, "message": "Licença salva no servidor online com sucesso"}
        except Exception as e:
            try:
                online_session.rollback()
                online_session.close()
            except:
                pass
            return {"success": False, "message": f"Erro ao salvar licença no servidor online: {str(e)}"}