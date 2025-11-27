import sqlite3
import sys

def update_database():
    try:
        # Conectar ao banco de dados
        conn = sqlite3.connect('instance/app.db')
        cursor = conn.cursor()

        # Verificar se a coluna user_type já existe na tabela license
        cursor.execute("PRAGMA table_info(license)")
        columns = [column[1] for column in cursor.fetchall()]

        if 'user_type' not in columns:
            # Adicionar a coluna user_type à tabela license
            cursor.execute('ALTER TABLE license ADD COLUMN user_type TEXT DEFAULT "user"')
            print("Coluna 'user_type' adicionada com sucesso à tabela 'license'.")
        else:
            print("Coluna 'user_type' já existe na tabela 'license'.")

        # Commit e fechar conexão
        conn.commit()
        conn.close()

        print("Banco de dados atualizado com sucesso!")
        return True

    except Exception as e:
        print(f"Erro ao atualizar o banco de dados: {str(e)}")
        return False

if __name__ == "__main__":
    if update_database():
        print("Atualização do banco de dados concluída.")
    else:
        print("Falha na atualização do banco de dados.")
        sys.exit(1)