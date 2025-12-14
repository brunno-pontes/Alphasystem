#!/bin/bash

# Script para iniciar o Alphasystem com ngrok

# Iniciar o aplicativo Flask em segundo plano
cd /home/brunno/Músicas/Alphasystem/sistema_prateleira
source ./venv/bin/activate
nohup python run.py > app.log 2>&1 &

# Aguardar um pouco para o aplicativo iniciar
sleep 5

# Iniciar o ngrok para expor o aplicativo web
ngrok http 5007 > ngrok_web.log 2>&1 &

# Aguardar para o ngrok iniciar
sleep 5

# Iniciar o ngrok para expor o MySQL (mesmo que o serviço não esteja funcionando agora)
ngrok tcp 3306 > ngrok_mysql.log 2>&1 &

echo "Alphasystem iniciado com ngrok!"
echo "URL Web: $(curl -s http://localhost:4040/api/tunnels | python3 -c 'import sys, json; data=json.load(sys.stdin); print([t[\"public_url\"] for t in data[\"tunnels\"] if \"http\" in t[\"proto\"]][0])' 2>/dev/null || echo 'não disponível')"
echo "Túnel MySQL: $(curl -s http://localhost:4040/api/tunnels | python3 -c 'import sys, json; data=json.load(sys.stdin); print([t[\"public_url\"] for t in data[\"tunnels\"] if \"tcp\" in t[\"proto\"]][0])' 2>/dev/null || echo 'não disponível')"

# Manter o script ativo
wait