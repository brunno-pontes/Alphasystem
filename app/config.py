import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import QueuePool

import urllib.parse

class DatabaseConfig:
    """Configuração do banco de dados"""

    # Força o uso do DATABASE_URL primeiro, e garante que MariaDB seja usado
    DATABASE_URL = os.environ.get('DATABASE_URL')

    if DATABASE_URL and ('mysql' in DATABASE_URL.lower() or 'mariadb' in DATABASE_URL.lower()):
        # Usa DATABASE_URL se estiver definido e for MariaDB/MySQL
        SQLALCHEMY_DATABASE_URI = DATABASE_URL
    else:
        # Configuração do MariaDB usando variáveis separadas
        DB_USER = os.environ.get('DB_USER', 'root')
        DB_PASSWORD = urllib.parse.quote_plus(os.environ.get('DB_PASSWORD', 'Rootbr@10!'))  # Codifica caracteres especiais
        DB_HOST = os.environ.get('DB_HOST', 'localhost')
        DB_PORT = os.environ.get('DB_PORT', '3306')
        DB_NAME = os.environ.get('DB_NAME', 'alpha')

        # URI de conexão com MariaDB
        SQLALCHEMY_DATABASE_URI = f'mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'

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