import os
from dotenv import load_dotenv

# Carregar variáveis de ambiente do arquivo .env ANTES de importar outros módulos
load_dotenv()

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from app.config import DevelopmentConfig
from flask_wtf.csrf import CSRFProtect

# Inicializar extensões
db = SQLAlchemy()
login_manager = LoginManager()
csrf = CSRFProtect()

def create_app():
    app = Flask(__name__)

    # Carregar configurações
    app.config.from_object(DevelopmentConfig)
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY') or 'sua_chave_secreta_aqui'

    # Configurar SQLAlchemy para usar o banco de dados local por padrão
    app.config['SQLALCHEMY_DATABASE_URI'] = DevelopmentConfig.LOCAL_DATABASE_URI
    app.config['SQLALCHEMY_BINDS'] = {
        'local': DevelopmentConfig.LOCAL_DATABASE_URI,
        'online': DevelopmentConfig.ONLINE_DATABASE_URI
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

    return app