from flask_login import UserMixin
from app import db, login_manager
from datetime import datetime
import hashlib
import secrets

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    role = db.Column(db.String(50), default='user')  # 'admin', 'manager', 'user'
    license_key = db.Column(db.String(255), db.ForeignKey('license.license_key'), nullable=True)
    manager_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)  # Para usuários gerenciados por um gerente
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relacionamento com o gerente
    manager = db.relationship('User', remote_side=[id], backref='managed_users')

class Product(db.Model):
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

class Sale(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    total_price = db.Column(db.Float, nullable=False)
    sale_date = db.Column(db.DateTime, default=datetime.utcnow)
    cashier_id = db.Column(db.Integer, db.ForeignKey('cashier.id'), nullable=True)  # Novo campo
    product = db.relationship('Product', backref='sales')
    cashier = db.relationship('Cashier', backref='sales')  # Novo relacionamento


class Cashier(db.Model):
    """Modelo para controle de caixa"""
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
    id = db.Column(db.Integer, primary_key=True)
    cashier_id = db.Column(db.Integer, db.ForeignKey('cashier.id'), nullable=False)
    transaction_type = db.Column(db.String(20), nullable=False)  # 'sale', 'expense', 'entry', 'exit'
    amount = db.Column(db.Float, nullable=False)
    description = db.Column(db.String(200))
    transaction_date = db.Column(db.DateTime, default=datetime.utcnow)
    related_sale_id = db.Column(db.Integer, db.ForeignKey('sale.id'), nullable=True)
    cashier = db.relationship('Cashier', backref='transactions')
    related_sale = db.relationship('Sale', backref='cashier_transactions')



class License(db.Model):
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