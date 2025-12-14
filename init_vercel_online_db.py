#!/usr/bin/env python3
"""
Script para inicializar o banco de dados online no Vercel (para validação de licenças)
Este script pode ser chamado durante o processo de deploy ou como uma tarefa separada.
"""
import os
import sys
from dotenv import load_dotenv

# Carregar variáveis de ambiente do arquivo .env (útil para testes locais)
# No Vercel, as variáveis já estarão disponíveis como variáveis de ambiente
if os.path.exists('.env'):
    load_dotenv()

def init_online_db():
    """Inicializa o banco de dados online com a tabela de licenças"""
    try:
        from app.database_manager import database_manager
        from sqlalchemy import text

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

def init_online_db_with_retry():
    """Inicializa o banco de dados online com tentativas de retry"""
    max_retries = 3
    for attempt in range(max_retries):
        print(f"Tentativa {attempt + 1} de {max_retries} para inicializar o banco online...")
        try:
            success = init_online_db()
            if success:
                return True
        except Exception as e:
            print(f"Tentativa {attempt + 1} falhou: {e}")
            if attempt == max_retries - 1:
                print("Todas as tentativas falharam.")
                return False
    return False

if __name__ == "__main__":
    print("=== Inicializando Banco de Dados Online para Vercel ===")
    success = init_online_db_with_retry()
    if success:
        print("✓ Banco de dados online inicializado com sucesso!")
        sys.exit(0)
    else:
        print("✗ Erro na inicialização do banco de dados online!")
        sys.exit(1)