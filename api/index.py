# Arquivo de compatibilidade com Vercel
import sys
import os

# Adiciona o diretório raiz ao path para permitir imports relativos
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from run import app

# O Vercel espera que a aplicação Flask esteja disponível como 'app'
application = app

# Para deploys no Vercel, usar apenas a aplicação Flask
if __name__ == "__main__":
    app.run()