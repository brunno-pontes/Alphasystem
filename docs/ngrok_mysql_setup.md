# Configuração do Ngrok para Expor o Banco de Dados MySQL

## 1. Instalação do Ngrok

### Opção 1: Instalar via gerenciador de pacotes
```bash
# Ubuntu/Debian
wget https://bin.equinox.io/c/4VmDzA7iaHb/ngrok-stable-linux-amd64.zip
unzip ngrok-stable-linux-amd64.zip
sudo mv ngrok /usr/local/bin/
```

### Opção 2: Instalar via snap
```bash
sudo snap install ngrok
```

## 2. Configuração do Ngrok

### Autenticação (recomendado para uso contínuo)
1. Crie uma conta em https://ngrok.com/
2. Obtenha seu token de autenticação no dashboard
3. Execute o comando com seu token:
```bash
ngrok config add-authtoken SEU_TOKEN_AQUI
```

## 3. Expondo o Banco de Dados MySQL

### Iniciar o túnel para o MySQL (porta 3306)
```bash
ngrok tcp 3306
```

### Exemplo de saída esperada:
```
Session Status                online
Account                       seu@email.com (Plan: Free)
Version                       3.x.x
Region                        United States (us)
Forwarding                    tcp://0.tcp.ngrok.io:12345 -> localhost:3306
```

Onde `0.tcp.ngrok.io:12345` é o host e porta externos que você usará para acessar seu banco de dados MySQL.

## 4. Configuração no Arquivo .env

Com o túnel ativo, configure as variáveis de ambiente:

```env
# Banco de dados local (acessado remotamente via ngrok)
LOCAL_DB_USER=seu_usuario_local
LOCAL_DB_PASSWORD=sua_senha_local
LOCAL_DB_HOST=0.tcp.ngrok.io  # Host fornecido pelo ngrok
LOCAL_DB_PORT=12345           # Porta fornecida pelo ngrok
LOCAL_DB_NAME=alpha_local

# Banco de dados online (para validação de licenças)
ONLINE_DB_USER=seu_usuario_online
ONLINE_DB_PASSWORD=sua_senha_online
ONLINE_DB_HOST=seu_host_online  # Pode ser um provedor MySQL como PlanetScale, AWS RDS, etc.
ONLINE_DB_PORT=3306
ONLINE_DB_NAME=alpha_online
```

## 5. Configuração do MySQL para Acesso Remoto

Certifique-se de que seu MySQL está configurado para aceitar conexões remotas:

### 1. Configurar o MySQL para aceitar conexões externas
Edite o arquivo de configuração do MySQL (geralmente `my.cnf` ou `my.ini`):

```ini
[mysqld]
bind-address = 0.0.0.0
```

### 2. Criar usuário com acesso remoto
Conecte-se ao MySQL e execute:
```sql
CREATE USER 'seu_usuario'@'%' IDENTIFIED BY 'sua_senha_segura';
GRANT ALL PRIVILEGES ON alpha_local.* TO 'seu_usuario'@'%';
FLUSH PRIVILEGES;
```

### 3. Reiniciar o serviço MySQL
```bash
sudo systemctl restart mysql
# ou
sudo systemctl restart mariadb
```

## 6. Considerações de Segurança

### Importante:
- **Nunca use senhas fracas ou padrões**
- **Limite o acesso por IP sempre que possível**
- **Use senhas fortes e únicas para o banco de dados**
- **Monitore o uso do ngrok regularmente**
- **Desative os túneis quando não estiverem em uso**

### Melhores práticas:
- Configure autenticação de dois fatores no ngrok
- Use credenciais específicas para acesso remoto (não as mesmas do acesso local)
- Considere o uso de um túnel privado (não gratuito) para produção
- Use VPN para aumentar a segurança se possível

## 7. Script de Inicialização com Ngrok

Crie um script para iniciar o sistema com o ngrok:

```bash
#!/bin/bash
# iniciar_com_ngrok.sh

echo "Iniciando Alphasystem com túneis ngrok..."

# Iniciar o aplicativo Flask em segundo plano
cd /caminho/para/seu/projeto
source ./venv/bin/activate
nohup python run.py > app.log 2>&1 &

# Aguardar um pouco para o aplicativo iniciar
sleep 5

# Iniciar o ngrok para expor o aplicativo web
ngrok http 5007 > ngrok_web.log 2>&1 &

# Aguardar para o ngrok iniciar
sleep 5

# Iniciar o ngrok para expor o MySQL
ngrok tcp 3306 > ngrok_mysql.log 2>&1 &

sleep 3

echo "Alphasystem com túneis ngrok iniciado!"
echo "URL Web: $(curl -s http://localhost:4040/api/tunnels | python3 -c 'import sys, json; data=json.load(sys.stdin); print([t["public_url"] for t in data["tunnels"] if "http" in t["proto"]][0])' 2>/dev/null || echo 'não disponível')"
echo "Túnel MySQL: $(curl -s http://localhost:4040/api/tunnels | python3 -c 'import sys, json; data=json.load(sys.stdin); print([t["public_url"] for t in data["tunnels"] if "tcp" in t["proto"]][0])' 2>/dev/null || echo 'não disponível')"

# Deixe o script rodando
wait
```

## 8. Testando a Conexão Remota

Para testar se a conexão remota está funcionando:

```bash
# Testar conexão com o MySQL via túnel ngrok
mysql -h 0.tcp.ngrok.io -P 12345 -u seu_usuario -p

# Alternativamente, com Python:
python -c "
import pymysql
connection = pymysql.connect(
    host='0.tcp.ngrok.io',
    port=12345,
    user='seu_usuario',
    password='sua_senha',
    database='alpha_local'
)
print('Conexão bem sucedida!')
connection.close()
"
```

## 9. Solução de Problemas

### Conexão recusada
- Verifique se o serviço MySQL está rodando
- Confirme que `bind-address` está configurado corretamente
- Verifique se não há regras de firewall bloqueando a porta

### Túnel ngrok não aparece
- Verifique se o ngrok está rodando (ps aux | grep ngrok)
- Confirme que seu token de autenticação está correto
- Verifique sua conexão com a internet

### Permissões de usuário no MySQL
- Verifique se o usuário tem permissões para conexões remotas
- Confirme que o usuário foi criado com host '%' ou o IP específico