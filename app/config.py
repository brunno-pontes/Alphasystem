import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import QueuePool

import urllib.parse

class DatabaseConfig:
    """Configuração do banco de dados"""

    # Configuração do banco de dados local
    LOCAL_DB_USER = os.environ.get('LOCAL_DB_USER', os.environ.get('DB_USER'))
    LOCAL_DB_PASSWORD_RAW = os.environ.get('LOCAL_DB_PASSWORD', os.environ.get('DB_PASSWORD'))

    # Codifica caracteres especiais apenas se não estiverem codificados
    if LOCAL_DB_PASSWORD_RAW is not None:
        if '%40' in LOCAL_DB_PASSWORD_RAW or '%40' in repr(LOCAL_DB_PASSWORD_RAW):
            # Se já estiver codificada, usar diretamente
            LOCAL_DB_PASSWORD = LOCAL_DB_PASSWORD_RAW
        else:
            # Caso contrário, codificar
            LOCAL_DB_PASSWORD = urllib.parse.quote_plus(LOCAL_DB_PASSWORD_RAW)
    else:
        # Deixar como None para ser validado em tempo de uso
        LOCAL_DB_PASSWORD = None

    LOCAL_DB_HOST = os.environ.get('LOCAL_DB_HOST', os.environ.get('DB_HOST', 'localhost'))
    LOCAL_DB_PORT = os.environ.get('LOCAL_DB_PORT', os.environ.get('DB_PORT', '3306'))
    LOCAL_DB_NAME = os.environ.get('LOCAL_DB_NAME', os.environ.get('DB_NAME', 'alpha_local'))

    # Montar LOCAL_DATABASE_URI somente quando todos os valores necessários estiverem disponíveis
    @classmethod
    def get_local_database_uri(cls):
        if not cls.LOCAL_DB_USER:
            raise ValueError("LOCAL_DB_USER ou DB_USER não está definido nas variáveis de ambiente.")
        if not cls.LOCAL_DB_PASSWORD_RAW:
            raise ValueError("LOCAL_DB_PASSWORD ou DB_PASSWORD não está definido nas variáveis de ambiente.")
        return f'mysql+pymysql://{cls.LOCAL_DB_USER}:{cls.LOCAL_DB_PASSWORD}@{cls.LOCAL_DB_HOST}:{cls.LOCAL_DB_PORT}/{cls.LOCAL_DB_NAME}'

    # Configuração do banco de dados online para validação de licenças
    ONLINE_DB_USER = os.environ.get('ONLINE_DB_USER', os.environ.get('DB_USER'))
    ONLINE_DB_PASSWORD_RAW = os.environ.get('ONLINE_DB_PASSWORD', os.environ.get('DB_PASSWORD'))

    # Codifica caracteres especiais apenas se não estiverem codificados
    if ONLINE_DB_PASSWORD_RAW is not None:
        if '%40' in ONLINE_DB_PASSWORD_RAW or '%40' in repr(ONLINE_DB_PASSWORD_RAW):
            # Se já estiver codificada, usar diretamente
            ONLINE_DB_PASSWORD = ONLINE_DB_PASSWORD_RAW
        else:
            # Caso contrário, codificar
            ONLINE_DB_PASSWORD = urllib.parse.quote_plus(ONLINE_DB_PASSWORD_RAW)
    else:
        # Deixar como None para ser validado em tempo de uso
        ONLINE_DB_PASSWORD = None

    ONLINE_DB_HOST = os.environ.get('ONLINE_DB_HOST', 'localhost')
    ONLINE_DB_PORT = os.environ.get('ONLINE_DB_PORT', '3306')
    ONLINE_DB_NAME = os.environ.get('ONLINE_DB_NAME', 'alpha_online')

    # Montar ONLINE_DATABASE_URI somente quando todos os valores necessários estiverem disponíveis
    @classmethod
    def get_online_database_uri(cls):
        if not cls.ONLINE_DB_USER:
            raise ValueError("ONLINE_DB_USER ou DB_USER não está definido nas variáveis de ambiente.")
        if not cls.ONLINE_DB_PASSWORD_RAW:
            raise ValueError("ONLINE_DB_PASSWORD ou DB_PASSWORD não está definido nas variáveis de ambiente.")
        return f'mysql+pymysql://{cls.ONLINE_DB_USER}:{cls.ONLINE_DB_PASSWORD}@{cls.ONLINE_DB_HOST}:{cls.ONLINE_DB_PORT}/{cls.ONLINE_DB_NAME}'

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
    @staticmethod
    def get_database_uri():
        return DatabaseConfig.get_local_database_uri()

# Configuração do ambiente de produção
class ProductionConfig(DatabaseConfig):
    DEBUG = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # Mantém compatibilidade com configuração existente
    @staticmethod
    def get_database_uri():
        return DatabaseConfig.get_local_database_uri()