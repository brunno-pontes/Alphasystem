#!/usr/bin/env python3
"""
Script para inicializar o banco de dados online (alpha_licenca) com as tabelas necessárias
"""
import os
import sys
from dotenv import load_dotenv
load_dotenv()

def init_online_db():
    """Inicializa o banco de dados online com todas as tabelas necessárias"""
    try:
        from app import create_app
        from app.database_manager import database_manager
        from sqlalchemy import text
        
        app = create_app()
        
        with app.app_context():
            print("Conectando ao banco de dados online...")
            
            # Obter engine e conexão com o banco online
            online_engine = database_manager.get_online_engine()
            
            # Criar as tabelas necessárias no banco online
            print("Criando tabelas no banco online...")
            
            # Tabela license
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
                last_validation DATETIME DEFAULT CURRENT_TIMESTAMP
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

def check_online_structure():
    """Verifica a estrutura do banco online"""
    try:
        from app.database_manager import database_manager
        from sqlalchemy import text
        
        online_engine = database_manager.get_online_engine()
        
        with online_engine.connect() as conn:
            # Listar tabelas no banco online
            tables_result = conn.execute(text("SHOW TABLES")).fetchall()
            print(f"\nTabelas no banco online:")
            for table in tables_result:
                print(f"  - {table[0]}")
            
            # Se tiver tabela license, mostrar sua estrutura
            if any(table[0] == 'license' for table in tables_result):
                print(f"\nEstrutura da tabela 'license':")
                structure_result = conn.execute(text("DESCRIBE license")).fetchall()
                for column in structure_result:
                    print(f"  {column[0]}: {column[1]} {column[2]} {column[4] or ''}")
            
    except Exception as e:
        print(f"Erro ao verificar estrutura do banco online: {e}")

if __name__ == "__main__":
    print("=== Inicializando Banco de Dados Online ===")
    init_online_db()
    print("\n=== Verificando Estrutura ===")
    check_online_structure()