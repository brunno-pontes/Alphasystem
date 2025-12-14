#!/usr/bin/env python3
"""
Script para inicializar o banco de dados online no Vercel (para validação de licenças)
"""
import os
import sys
from dotenv import load_dotenv
load_dotenv()

def init_online_db():
    """Inicializa o banco de dados online com a tabela de licenças"""
    try:
        from app.database_manager import database_manager
        from sqlalchemy import text
        from app.config import DatabaseConfig  # Importar a config para forçar leitura das variáveis

        print("Conectando ao banco de dados online para inicialização...")

        # Obter engine e conexão com o banco online
        online_engine = database_manager.get_online_engine()

        # Criar a tabela license no banco online
        print("Criando/atualizando tabela de licenças no banco online...")

        create_license_table = """
        CREATE TABLE IF NOT EXISTS license (
            id INT AUTO_INCREMENT PRIMARY KEY,
            license_key VARCHAR(255) UNIQUE NOT NULL,
            client_name VARCHAR(200) NOT NULL,
            client_email VARCHAR(200) NOT NULL,
            expiry_date DATETIME NOT NULL,
            is_active BOOLEAN DEFAULT TRUE,
            user_type VARCHAR(20) DEFAULT 'user',
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            last_validation DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
        );
        """

        with online_engine.connect() as conn:
            conn.execute(text(create_license_table))
            conn.commit()

        print("Tabela 'license' criada/atualizada no banco online com sucesso!")

        # Verificar se a tabela foi criada
        with online_engine.connect() as conn:
            result = conn.execute(text("SHOW TABLES LIKE 'license'")).fetchone()
            if result:
                print("✓ Tabela 'license' confirmada no banco online")
            else:
                print("✗ Erro: Tabela 'license' não encontrada no banco online")

        print("Banco de dados online inicializado com sucesso!")

    except Exception as e:
        print(f"Erro ao inicializar o banco de dados online: {e}")
        import traceback
        traceback.print_exc()
        return False

    return True

if __name__ == "__main__":
    print("=== Inicializando Banco de Dados Online para Vercel ===")
    success = init_online_db()
    if success:
        print("✓ Banco de dados online inicializado com sucesso!")
        sys.exit(0)
    else:
        print("✗ Erro na inicialização do banco de dados online!")
        sys.exit(1)