"""
Script para adicionar a coluna cashier_id à tabela de vendas no banco de dados SQLite
"""
import sqlite3
import os

def add_cashier_id_column():
    # Obter o caminho do banco de dados
    db_path = os.path.join(os.getcwd(), 'instance', 'app.db')
    
    if not os.path.exists(db_path):
        print(f"Banco de dados não encontrado: {db_path}")
        return
    
    try:
        # Conectar ao banco de dados
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Verificar se a coluna já existe
        cursor.execute("PRAGMA table_info(sale)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'cashier_id' in columns:
            print("Coluna cashier_id já existe na tabela sale")
        else:
            # Adicionar a coluna cashier_id à tabela sale
            cursor.execute("ALTER TABLE sale ADD COLUMN cashier_id INTEGER")
            print("Coluna cashier_id adicionada com sucesso à tabela sale")
        
        conn.commit()
        conn.close()
        print("Script executado com sucesso!")
        
    except Exception as e:
        print(f"Erro ao executar o script: {e}")

if __name__ == "__main__":
    add_cashier_id_column()