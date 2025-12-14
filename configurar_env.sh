#!/bin/bash

# Script para configurar variáveis de ambiente no Vercel
# Execute este script para adicionar as variáveis de ambiente necessárias

echo "Configurando variáveis de ambiente no Vercel..."

# Adicionei a chave secreta gerada
echo "Primeiro, adicione manualmente a SECRET_KEY:"
echo "Execute: npx vercel env add SECRET_KEY"
echo "E cole este valor: YXkUsN4Rfn4gwEXJ7Z7JlJ9ozUsDs7u30bmTDeV1Rd8"
echo ""

echo "Depois adicione as seguintes variáveis (em ordem):"

variables=(
    "LOCAL_DB_USER"
    "LOCAL_DB_PASSWORD" 
    "LOCAL_DB_HOST"
    "LOCAL_DB_PORT"
    "LOCAL_DB_NAME"
    "ONLINE_DB_USER"
    "ONLINE_DB_PASSWORD"
    "ONLINE_DB_HOST"
    "ONLINE_DB_PORT"
    "ONLINE_DB_NAME"
    "ADMIN_USERNAME"
    "ADMIN_PASSWORD"
    "ADMIN_EMAIL"
    "EMAIL_HOST"
    "EMAIL_PORT"
    "EMAIL_HOST_USER"
    "EMAIL_HOST_PASSWORD"
    "PRATELEIRA_LICENSE_KEY"
)

for var in "${variables[@]}"; do
    echo "- $var"
done

echo ""
echo "Para adicionar cada variável, execute:"
echo "npx vercel env add NOME_DA_VARIAVEL"
echo ""
echo "Para o ambiente de produção, você precisará adicionar em:"
echo "npx vercel --prod"
echo "e selecionar 'Add Environment Variables'"