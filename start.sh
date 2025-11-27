#!/bin/bash

# Script de inicialização do Sistema Prateleira

echo "Iniciando o Sistema Prateleira..."

# Verificar se o ambiente virtual está ativo
if [[ "$VIRTUAL_ENV" == "" ]]; then
    echo "Ativando ambiente virtual..."
    source venv/bin/activate
fi

# Instalar dependências se necessário
if [ ! -d "venv" ]; then
    echo "Criando ambiente virtual..."
    python -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
else
    source venv/bin/activate
fi

# Executar o sistema
echo "Iniciando o servidor..."
python run.py