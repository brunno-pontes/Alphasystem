from app import db
from app.config import DevelopmentConfig
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import threading


class DatabaseManager:
    """
    Gerenciador de múltiplos bancos de dados para o sistema Alpha
    """
    _local_engines = {}
    _local_sessions = {}
    _lock = threading.Lock()

    @classmethod
    def get_local_engine(cls):
        """Obtém o engine para o banco de dados local"""
        thread_id = threading.get_ident()
        if thread_id not in cls._local_engines:
            with cls._lock:
                if thread_id not in cls._local_engines:
                    cls._local_engines[thread_id] = create_engine(
                        DevelopmentConfig.LOCAL_DATABASE_URI,
                        **DevelopmentConfig.LOCAL_ENGINE_OPTIONS
                    )
        return cls._local_engines[thread_id]

    @classmethod
    def get_online_engine(cls):
        """Obtém o engine para o banco de dados online"""
        return create_engine(
            DevelopmentConfig.ONLINE_DATABASE_URI,
            **DevelopmentConfig.ONLINE_ENGINE_OPTIONS
        )

    @classmethod
    def get_local_session(cls):
        """Obtém uma sessão para o banco de dados local"""
        thread_id = threading.get_ident()
        if thread_id not in cls._local_sessions:
            with cls._lock:
                if thread_id not in cls._local_sessions:
                    engine = cls.get_local_engine()
                    Session = sessionmaker(bind=engine)
                    cls._local_sessions[thread_id] = Session()
        return cls._local_sessions[thread_id]

    @classmethod
    def get_online_session(cls):
        """Obtém uma sessão para o banco de dados online"""
        engine = cls.get_online_engine()
        Session = sessionmaker(bind=engine)
        return Session()

    @classmethod
    def get_db_for_licenses(cls):
        """
        Retorna a sessão apropriada para operações com licenças.
        Por padrão, usa o banco local, mas permite validação online.
        """
        return db.session  # SQLAlchemy session padrão (local)

    @classmethod
    def get_online_db_session(cls):
        """
        Retorna uma sessão direta para o banco de dados online
        """
        return cls.get_online_session()


# Instância global do gerenciador de banco de dados
database_manager = DatabaseManager()