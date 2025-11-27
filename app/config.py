import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import QueuePool

class DatabaseConfig:
    """Configuração do banco de dados"""

    # Obter o caminho absoluto para o diretório raiz do projeto
    BASE_DIR = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))

    # Criar o caminho completo para o banco de dados
    DATABASE_PATH = os.path.join(BASE_DIR, 'instance', 'app.db')

    # Usar caminho absoluto para o banco de dados SQLite
    SQLALCHEMY_DATABASE_URI = f'sqlite:///{DATABASE_PATH}'

    # Opções adicionais para melhorar desempenho
    SQLALCHEMY_ENGINE_OPTIONS = {
        'poolclass': QueuePool,
        'pool_size': 10,
        'pool_recycle': 280,
        'pool_pre_ping': True,
        'max_overflow': 20
    }

    @staticmethod
    def test_connection():
        """Testa a conexão com o banco de dados"""
        try:
            engine = create_engine(DatabaseConfig.SQLALCHEMY_DATABASE_URI,
                                 **DatabaseConfig.SQLALCHEMY_ENGINE_OPTIONS)
            connection = engine.connect()
            connection.close()
            return True
        except Exception as e:
            print(f"Erro ao conectar ao banco de dados: {e}")
            return False

# Configuração do ambiente de desenvolvimento
class DevelopmentConfig(DatabaseConfig):
    DEBUG = True
    SQLALCHEMY_TRACK_MODIFICATIONS = False

# Configuração do ambiente de produção
class ProductionConfig(DatabaseConfig):
    DEBUG = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False