#!/bin/bash
# Script de inicialização do Alphasystem

echo "Alphasystem - Inicialização"

# Verificar se o arquivo .env existe
if [ ! -f ".env" ]; then
    echo "⚠️  Aviso: Arquivo .env não encontrado!"
    echo "Por favor, copie o arquivo .env.example para .env e configure suas credenciais:"
    echo "  cp .env.example .env"
    echo "  # Edite o arquivo .env com suas credenciais reais"
    echo ""
    echo "Configurações mínimas necessárias no arquivo .env:"
    echo "  - SECRET_KEY: uma chave secreta forte"
    echo "  - DB_USER e DB_PASSWORD: credenciais do banco de dados local"
    echo "  - ONLINE_DB_USER e ONLINE_DB_PASSWORD: credenciais do banco de dados online"
    echo "  - EMAIL_HOST_USER: seu email para envio de emails de recuperação"
    echo "  - EMAIL_HOST_PASSWORD: senha de app (não sua senha padrão)"
    echo ""
    echo "Para mais informações, consulte o README.md"
    exit 1
fi

echo "✅ Arquivo .env encontrado"

# Verificar se o ambiente virtual está ativo
if [ -z "$VIRTUAL_ENV" ]; then
    echo "⚠️  Aviso: Ambiente virtual não está ativo"
    echo "Ativando ambiente virtual..."
    if [ -d "venv" ]; then
        source venv/bin/activate
        echo "✅ Ambiente virtual ativado"
    else
        echo "❌ Erro: Diretório venv não encontrado"
        echo "Crie o ambiente virtual com: python -m venv venv"
        exit 1
    fi
else
    echo "✅ Ambiente virtual já está ativo"
fi

# Instalar dependências se necessário
echo "Instalando dependências..."
pip install -r requirements.txt

# Iniciar o sistema
echo "Iniciando o sistema..."
# O script init_admin_mariadb.py já está embutido na inicialização do run.py
python run.py