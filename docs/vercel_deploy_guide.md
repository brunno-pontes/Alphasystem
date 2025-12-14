# Deploy no Vercel com MySQL e Ngrok

Este guia explica como fazer o deploy do Alphasystem no Vercel com MySQL, usando ngrok para expor o banco de dados online.

## 1. Configuração Inicial

### 1.1 Preparar o repositório
1. Faça fork deste repositório no GitHub
2. Clone o repositório para sua máquina local
3. Configure as variáveis de ambiente conforme descrito abaixo

### 1.2 Instalar ngrok
Siga as instruções em `docs/ngrok_mysql_setup.md` para instalar e configurar o ngrok com sua conta.

## 2. Configuração das Variáveis de Ambiente

### 2.1 Criar o arquivo .env.local
```bash
cp .env.example .env.local
```

### 2.2 Configurar as variáveis
Edite o `.env.local` com as seguintes informações:

```env
# Chave secreta (gerar com: python -c "import secrets; print(secrets.token_urlsafe(32))")
SECRET_KEY=sua_chave_secreta_gerada_aqui

# Banco de dados local (acessado remotamente via ngrok ou provedor externo)
LOCAL_DB_USER=seu_usuario_local
LOCAL_DB_PASSWORD=sua_senha_local
LOCAL_DB_HOST=seu_host_ou_ngrok  # Ex: abc123.ngrok.io ou IP público
LOCAL_DB_PORT=3306
LOCAL_DB_NAME=alpha_local

# Banco de dados online (para validação de licenças)
ONLINE_DB_USER=seu_usuario_online
ONLINE_DB_PASSWORD=sua_senha_online
ONLINE_DB_HOST=host_provedor_bd_online  # Ex: provedor externo ou outro túnel ngrok
ONLINE_DB_PORT=3306
ONLINE_DB_NAME=alpha_online

# Configurações de administrador (opcionais)
ADMIN_USERNAME=admin
ADMIN_PASSWORD=sua_senha_admin
ADMIN_EMAIL=seu_email@empresa.com

# Configurações de email (para recuperação de senha)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=seu_email@gmail.com
EMAIL_HOST_PASSWORD=sua_senha_de_app
```

### 2.3 Importante sobre os bancos de dados
- **Banco Local** (local): Armazena os dados operacionais do sistema (usuários, produtos, vendas, caixas, etc.)
- **Banco Online** (online): Usado exclusivamente para validação de licenças

## 3. Configuração do Banco de Dados Local com Ngrok

### 3.1 Iniciar o MySQL local
Certifique-se de que o MySQL/MariaDB está rodando localmente e configurado para aceitar conexões remotas (veja `docs/ngrok_mysql_setup.md`).

### 3.2 Iniciar os túneis ngrok
Execute o script de inicialização com ngrok:

```bash
# Iniciar o sistema e os túneis ngrok
./iniciar_ngrok.sh
```

Ou execute manualmente:
```bash
# Iniciar o aplicativo Flask
python run.py &

# Iniciar o túnel para web (opcional, para testes locais)
ngrok http 5007 &

# Iniciar o túnel para MySQL
ngrok tcp 3306 &
```

Copie os endpoints fornecidos pelo ngrok (ex: `0.tcp.ngrok.io:12345`) para usar como `LOCAL_DB_HOST` e `LOCAL_DB_PORT`.

## 4. Importar Variáveis para o Vercel

### 4.1 Instalar o CLI do Vercel
```bash
npm install -g vercel
```

### 4.2 Fazer login
```bash
vercel login
```

### 4.3 Importar variáveis de ambiente
```bash
vercel env add
```

Você precisará adicionar cada variável de ambiente listada acima no Vercel. O comando irá pedir cada variável individualmente.

Alternativamente, você pode usar um arquivo:
```bash
vercel env pull .vercel_env
# Em seguida edite manualmente no painel do Vercel
```

## 5. Configuração do vercel.json

O arquivo `vercel.json` já está configurado corretamente:

```json
{
  "version": 2,
  "name": "alphasystem",
  "builds": [
    {
      "src": "api/index.py",
      "use": "@vercel/python",
      "config": {
        "runtime": "python3.9"
      }
    }
  ],
  "routes": [
    {
      "src": "/(.*)",
      "dest": "api/index.py"
    }
  ],
  "env": {
    "FLASK_ENV": "production"
  }
}
```

## 6. Deploy Inicial

### 6.1 Fazer o deploy
```bash
vercel --prod
```

### 6.2 Opcional: Nomear o projeto
Durante o primeiro deploy, você pode escolher um nome para o projeto ou usar o nome gerado automaticamente.

## 7. Configuração Pós-Deploy

### 7.1 Inicializar o banco de dados online
Após o deploy, você pode precisar rodar o script de inicialização do banco de dados online:

```bash
# Executar localmente após configurar as variáveis corretas
python api/init_db.py
```

Ou adicione esta execução como parte do processo de build no Vercel.

### 7.2 Script de build para inicialização do banco
Você pode adicionar um script de build no `vercel.json`:

```json
{
  "version": 2,
  "name": "alphasystem",
  "builds": [
    {
      "src": "api/index.py",
      "use": "@vercel/python",
      "config": {
        "runtime": "python3.9"
      }
    }
  ],
  "routes": [
    {
      "src": "/(.*)",
      "dest": "api/index.py"
    }
  ],
  "env": {
    "FLASK_ENV": "production"
  },
  "build": {
    "env": {
      "BUILD_DUMMY": "1"
    }
  }
}
```

## 8. Integração Contínua

### 8.1 Conectar ao GitHub
1. Acesse o painel do Vercel
2. Conecte sua conta do GitHub
3. Importe o repositório do Alphasystem
4. As variáveis de ambiente já estarão configuradas
5. Cada push para o repositório irá disparar um novo deploy

### 8.2 Configurações recomendadas no Vercel
- **Framework Preset**: None/Other
- **Root Directory**: Deixe em branco
- **Build Command**: Deixe em branco (o Vercel detecta automaticamente)
- **Output Directory**: Deixe em branco
- **Install Command**: Deixe em branco

## 9. Considerações de Segurança

### 9.1 Segurança do banco de dados
- Use senhas fortes para os usuários do banco de dados
- Limite o acesso por IP sempre que possível
- Não compartilhe credenciais de banco de dados em repositórios públicos
- Use variáveis de ambiente para todas as credenciais

### 9.2 Segurança do ngrok
- Não compartilhe URLs do ngrok publicamente
- Use autenticação no ngrok para controle de uso
- Monitore o dashboard do ngrok regularmente
- Desative túneis que não estão em uso

## 10. Solução de Problemas

### 10.1 Erros comuns de deploy
- **Erro de dependências**: Verifique se todas as dependências estão em `requirements.txt`
- **Erro de banco de dados**: Verifique as credenciais e se o host está acessível
- **Erro de timeout**: Certifique-se de que o aplicativo está respondendo em tempo hábil

### 10.2 Verificação de status
1. Acesse o log do deploy no painel do Vercel
2. Verifique se todas as variáveis de ambiente estão configuradas
3. Teste manualmente as conexões com os bancos de dados

### 10.3 Teste de conexão
Use o script de teste de conexão com o banco de dados para verificar se as configurações estão corretas.

## 11. Processo de Validação de Licenças

Depois do deploy, o sistema funcionará da seguinte forma:
1. Os usuários do sistema local terão acesso controlado por licenças
2. A cada 30 dias, o sistema validará a licença no banco de dados online
3. Em caso de falha na validação, há um período de carência de 3 dias
4. Após o período de carência, o acesso é bloqueado até a validação ser bem sucedida

## 12. Monitoramento e Manutenção

### 12.1 Monitoramento
- Verifique regularmente os logs do Vercel
- Monitore o uso do ngrok
- Verifique a conectividade com os bancos de dados

### 12.2 Atualizações
- As atualizações no repositório GitHub irão disparar novos deploys automaticamente
- Teste sempre as atualizações em um ambiente de staging antes de ir para produção