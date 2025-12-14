import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import QueuePool
import urllib.parse

class DatabaseConfig:
    """Configuração do banco de dados"""

    @classmethod
    def get_local_database_uri(cls):
        """Obtém a URI do banco de dados local com tratamento de erros"""
        # Configuração do banco de dados local
        LOCAL_DB_USER = os.environ.get('LOCAL_DB_USER', os.environ.get('DB_USER'))
        LOCAL_DB_PASSWORD_RAW = os.environ.get('LOCAL_DB_PASSWORD', os.environ.get('DB_PASSWORD'))

        # Verifica se as variáveis críticas estão definidas
        if not LOCAL_DB_USER:
            raise ValueError("LOCAL_DB_USER ou DB_USER não está definido nas variáveis de ambiente.")
        if not LOCAL_DB_PASSWORD_RAW:
            raise ValueError("LOCAL_DB_PASSWORD ou DB_PASSWORD não está definido nas variáveis de ambiente.")

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

        # Tratar LOCAL_DB_PORT - garantir que é um número
        LOCAL_DB_PORT_RAW = os.environ.get('LOCAL_DB_PORT', os.environ.get('DB_PORT', '3306'))
        try:
            LOCAL_DB_PORT = int(LOCAL_DB_PORT_RAW)  # Converte para inteiro
        except ValueError:
            # Se não for um número, usar valor padrão
            LOCAL_DB_PORT = 3306

        LOCAL_DB_NAME = os.environ.get('LOCAL_DB_NAME', os.environ.get('DB_NAME', 'alpha_local'))

        return f'mysql+pymysql://{LOCAL_DB_USER}:{LOCAL_DB_PASSWORD}@{LOCAL_DB_HOST}:{LOCAL_DB_PORT}/{LOCAL_DB_NAME}'

    @classmethod
    def get_online_database_uri(cls):
        """Obtém a URI do banco de dados online com tratamento de erros"""
        # Configuração do banco de dados online para validação de licenças
        ONLINE_DB_USER = os.environ.get('ONLINE_DB_USER', os.environ.get('DB_USER'))
        ONLINE_DB_PASSWORD_RAW = os.environ.get('ONLINE_DB_PASSWORD', os.environ.get('DB_PASSWORD'))

        # Verifica se as variáveis críticas estão definidas
        if not ONLINE_DB_USER:
            raise ValueError("ONLINE_DB_USER ou DB_USER não está definido nas variáveis de ambiente.")
        if not ONLINE_DB_PASSWORD_RAW:
            raise ValueError("ONLINE_DB_PASSWORD ou DB_PASSWORD não está definido nas variáveis de ambiente.")

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

        # Tratar ONLINE_DB_PORT - garantir que é um número
        ONLINE_DB_PORT_RAW = os.environ.get('ONLINE_DB_PORT', '3306')
        try:
            ONLINE_DB_PORT = int(ONLINE_DB_PORT_RAW)  # Converte para inteiro
        except ValueError:
            # Se não for um número, usar valor padrão
            ONLINE_DB_PORT = 3306

        ONLINE_DB_NAME = os.environ.get('ONLINE_DB_NAME', 'alpha_online')

        return f'mysql+pymysql://{ONLINE_DB_USER}:{ONLINE_DB_PASSWORD}@{ONLINE_DB_HOST}:{ONLINE_DB_PORT}/{ONLINE_DB_NAME}'

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

    @classmethod
    def test_local_connection(cls):
        """Testa a conexão com o banco de dados local"""
        try:
            engine = create_engine(cls.get_local_database_uri(), **cls.LOCAL_ENGINE_OPTIONS)
            connection = engine.connect()
            connection.close()
            return True
        except Exception as e:
            print(f"Erro ao conectar ao banco de dados local: {e}")
            return False

    @classmethod
    def test_online_connection(cls):
        """Testa a conexão com o banco de dados online"""
        try:
            engine = create_engine(cls.get_online_database_uri(), **cls.ONLINE_ENGINE_OPTIONS)
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