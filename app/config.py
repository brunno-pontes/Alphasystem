import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import QueuePool

import urllib.parse

class DatabaseConfig:
    """Configuração do banco de dados"""

    # Configuração do banco de dados local
    LOCAL_DB_USER = os.environ.get('LOCAL_DB_USER', os.environ.get('DB_USER', 'root'))
    LOCAL_DB_PASSWORD_RAW = os.environ.get('LOCAL_DB_PASSWORD', os.environ.get('DB_PASSWORD', 'Rootbr@10!'))
    # Codifica caracteres especiais apenas se não estiverem codificados
    if '%40' in LOCAL_DB_PASSWORD_RAW or '%40' in repr(LOCAL_DB_PASSWORD_RAW):
        # Se já estiver codificada, usar diretamente
        LOCAL_DB_PASSWORD = LOCAL_DB_PASSWORD_RAW
    else:
        # Caso contrário, codificar
        LOCAL_DB_PASSWORD = urllib.parse.quote_plus(LOCAL_DB_PASSWORD_RAW)
    LOCAL_DB_HOST = os.environ.get('LOCAL_DB_HOST', os.environ.get('DB_HOST', 'localhost'))
    LOCAL_DB_PORT = os.environ.get('LOCAL_DB_PORT', os.environ.get('DB_PORT', '3306'))
    LOCAL_DB_NAME = os.environ.get('LOCAL_DB_NAME', os.environ.get('DB_NAME', 'alpha_local'))

    LOCAL_DATABASE_URI = f'mysql+pymysql://{LOCAL_DB_USER}:{LOCAL_DB_PASSWORD}@{LOCAL_DB_HOST}:{LOCAL_DB_PORT}/{LOCAL_DB_NAME}'

    # Configuração do banco de dados online para validação de licenças
    ONLINE_DB_USER = os.environ.get('ONLINE_DB_USER', 'root')
    ONLINE_DB_PASSWORD_RAW = os.environ.get('ONLINE_DB_PASSWORD', 'Rootbr@10!')
    # Codifica caracteres especiais apenas se não estiverem codificados
    if '%40' in ONLINE_DB_PASSWORD_RAW or '%40' in repr(ONLINE_DB_PASSWORD_RAW):
        # Se já estiver codificada, usar diretamente
        ONLINE_DB_PASSWORD = ONLINE_DB_PASSWORD_RAW
    else:
        # Caso contrário, codificar
        ONLINE_DB_PASSWORD = urllib.parse.quote_plus(ONLINE_DB_PASSWORD_RAW)
    ONLINE_DB_HOST = os.environ.get('ONLINE_DB_HOST', 'localhost')
    ONLINE_DB_PORT = os.environ.get('ONLINE_DB_PORT', '3306')
    ONLINE_DB_NAME = os.environ.get('ONLINE_DB_NAME', 'alpha_online')

    ONLINE_DATABASE_URI = f'mysql+pymysql://{ONLINE_DB_USER}:{ONLINE_DB_PASSWORD}@{ONLINE_DB_HOST}:{ONLINE_DB_PORT}/{ONLINE_DB_NAME}'

    # Opções adicionais para melhorar desempenho
    LOCAL_ENGINE_OPTIONS = {
        'poolclass': QueuePool,
        'pool_size': 10,
        'pool_recycle': 280,
        'pool_pre_ping': True,
        'max_overflow': 20
    }

    ONLINE_ENGINE_OPTIONS = {
        'poolclass': QueuePool,
        'pool_size': 5,  # Menor pool para validações online
        'pool_recycle': 280,
        'pool_pre_ping': True,
        'max_overflow': 10
    }

    @staticmethod
    def test_local_connection():
        """Testa a conexão com o banco de dados local"""
        try:
            engine = create_engine(DatabaseConfig.LOCAL_DATABASE_URI,
                                 **DatabaseConfig.LOCAL_ENGINE_OPTIONS)
            connection = engine.connect()
            connection.close()
            return True
        except Exception as e:
            print(f"Erro ao conectar ao banco de dados local: {e}")
            return False

    @staticmethod
    def test_online_connection():
        """Testa a conexão com o banco de dados online"""
        try:
            engine = create_engine(DatabaseConfig.ONLINE_DATABASE_URI,
                                 **DatabaseConfig.ONLINE_ENGINE_OPTIONS)
            connection = engine.connect()
            connection.close()
            return True
        except Exception as e:
            print(f"Erro ao conectar ao banco de dados online: {e}")
            return False

# Configuração do ambiente de desenvolvimento
class DevelopmentConfig(DatabaseConfig):
    DEBUG = True
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # Mantém compatibilidade com configuração existente
    SQLALCHEMY_DATABASE_URI = DatabaseConfig.LOCAL_DATABASE_URI

# Configuração do ambiente de produção
class ProductionConfig(DatabaseConfig):
    DEBUG = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # Mantém compatibilidade com configuração existente
    SQLALCHEMY_DATABASE_URI = DatabaseConfig.LOCAL_DATABASE_URI