import os
from dotenv import load_dotenv

# Carregar variáveis de ambiente do arquivo .env ANTES de importar outros módulos
load_dotenv()

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from app.config import DevelopmentConfig, ProductionConfig
from flask_wtf.csrf import CSRFProtect
import logging

# Inicializar extensões
db = SQLAlchemy()
login_manager = LoginManager()
csrf = CSRFProtect()

def create_app():
    app = Flask(__name__)

    # Carregar configurações
    app.config.from_object(DevelopmentConfig)
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY') or 'sua_chave_secreta_aqui'

    # Tentar configurar o banco de dados local, com fallback para SQLite em caso de erro
    try:
        # Verificar se as variáveis essenciais do banco de dados estão definidas
        local_db_user = os.environ.get('LOCAL_DB_USER') or os.environ.get('DB_USER')
        local_db_password = os.environ.get('LOCAL_DB_PASSWORD') or os.environ.get('DB_PASSWORD')

        if local_db_user and local_db_password:
            app.config['SQLALCHEMY_DATABASE_URI'] = DevelopmentConfig.get_local_database_uri()
            app.config['SQLALCHEMY_BINDS'] = {
                'local': DevelopmentConfig.get_local_database_uri(),
                'online': DevelopmentConfig.get_online_database_uri()
            }
        else:
            raise ValueError("Variáveis de ambiente do banco de dados não configuradas")
    except (ValueError, TypeError) as e:
        # Em caso de erro nas variáveis de ambiente do banco de dados, usar SQLite para testes
        print(f"Erro nas variáveis de ambiente do banco de dados: {e}")
        print("Usando banco de dados SQLite para testes...")
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///fallback.db'
        app.config['SQLALCHEMY_BINDS'] = {
            'local': 'sqlite:///fallback_local.db',
            'online': 'sqlite:///fallback_online.db'
        }

    # Inicializar extensões com app
    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)  # Adiciona proteção CSRF
    login_manager.login_view = 'auth.login'

    # Definir o contexto do template para ter acesso ao current_user
    @app.context_processor
    def inject_user():
        from flask_login import current_user
        # Verificar se o usuário está autenticado via Flask-Login
        if current_user.is_authenticated:
            return dict(current_user=current_user)
        return dict(current_user=None)

    # Registrar blueprints
    from app.routes.main import bp as main_bp
    app.register_blueprint(main_bp)

    from app.routes.auth import bp as auth_bp
    app.register_blueprint(auth_bp)

    from app.routes.products import bp as products_bp
    app.register_blueprint(products_bp)

    from app.routes.sales import bp as sales_bp
    app.register_blueprint(sales_bp)

    from app.routes.cashier import bp as cashier_bp
    app.register_blueprint(cashier_bp)

    from app.routes.licenses import bp as licenses_bp
    app.register_blueprint(licenses_bp)

    from app.routes.manager import bp as manager_bp
    app.register_blueprint(manager_bp)

    from app.routes.registration import bp as registration_bp
    app.register_blueprint(registration_bp)

    from app.routes.credit import bp as credit_bp
    app.register_blueprint(credit_bp)

    # Registrar blueprint de debug (somente para desenvolvimento)
    try:
        from app.routes.debug import bp as debug_bp
        app.register_blueprint(debug_bp)
    except ImportError:
        pass

    # Adicionar tratamento de erro global para erros de banco de dados
    @app.errorhandler(Exception)
    def handle_exception(e):
        app.logger.error(f"Erro não tratado: {e}")
        return "Ocorreu um erro no servidor. Verifique as configurações do banco de dados.", 500

    return app