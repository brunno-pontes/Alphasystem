# Alphasystem

Sistema completo de gerenciamento de estoque e vendas com controle de licenças para instalação local.

## Funcionalidades

- Controle de estoque de produtos
- Registro de vendas
- Dashboard com estatísticas
- Sistema de licenças com validação mensal via internet
- Interface intuitiva e responsiva
- Controle de caixa moderno com preenchimento automático das vendas
- Dashboard gerencial com visão de todos os caixas abertos e resumo de vendas do dia

## Requisitos

- Python 3.8+
- MariaDB (ou MySQL)
- Pip

## Instalação

1. Clone ou crie o projeto:

```bash
cd alphasystem
```

2. Crie um ambiente virtual:

```bash
python -m venv venv
source venv/bin/activate  # No Linux/Mac
# ou
venv\Scripts\activate  # No Windows
```

3. Instale as dependências:

```bash
pip install -r requirements.txt
```

4. Configure o banco de dados MariaDB:

Primeiro, certifique-se de que o MariaDB está instalado e em execução em seu sistema:

```bash
# No Ubuntu/Debian:
sudo apt update
sudo apt install mariadb-server
sudo systemctl start mariadb
sudo systemctl enable mariadb

# Configure o acesso root:
sudo mysql_secure_installation
```

Agora, crie o banco de dados e o usuário para o Alphasystem. O nome de usuário e senha padrão são definidos no arquivo `.env`, que você criará posteriormente:

```bash
# Conecte-se ao MariaDB como root ou usuário com privilégios de administrador
sudo mysql -u root -p

# Dentro do console do MariaDB, execute (substituindo 'seu_usuario' e 'sua_senha' pelos valores reais):
CREATE USER 'seu_usuario'@'localhost' IDENTIFIED BY 'sua_senha';
CREATE DATABASE IF NOT EXISTS `alpha_local`;
GRANT ALL PRIVILEGES ON `alpha_local`.* TO 'seu_usuario'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

Se você encontrar o erro "Access denied for user 'seu_usuario'@'localhost'" ou "Column 'authentication_string' is not updatable", use os comandos apropriados para sua versão do MariaDB:

```bash
# Conecte-se ao MariaDB como root ou usuário com privilégios de administrador
sudo mysql -u root -p

# Dentro do console do MariaDB, execute os comandos apropriados para sua versão (substituindo 'seu_usuario' e 'sua_senha'):

# Para versões mais recentes do MariaDB:
CREATE USER 'seu_usuario'@'localhost' IDENTIFIED BY 'sua_senha';
CREATE DATABASE IF NOT EXISTS `alpha_local`;
GRANT ALL PRIVILEGES ON `alpha_local`.* TO 'seu_usuario'@'localhost';
FLUSH PRIVILEGES;

# Para versões mais antigas do MariaDB/MySQL (se CREATE USER não funcionar):
USE mysql;
CREATE USER 'seu_usuario'@'localhost' IDENTIFIED BY 'sua_senha';
CREATE DATABASE IF NOT EXISTS `alpha_local`;
GRANT ALL PRIVILEGES ON `alpha_local`.* TO 'seu_usuario'@'localhost';
FLUSH PRIVILEGES;

EXIT;
```

5. Execute o sistema:

```bash
python run.py
```

Na primeira execução, o sistema fará o seguinte automaticamente:
- Criará todas as tabelas necessárias no banco de dados
- Criará um usuário admin (se não existir) com as credenciais definidas no arquivo `.env` (ou usando os valores padrão `admin`/`admin123` se não forem definidas)

## Configuração da Licença

O sistema requer uma chave de licença válida que é validada mensalmente com o servidor central. A chave pode ser configurada de duas formas:

1. Através de variável de ambiente:
```bash
export PRATELEIRA_LICENSE_KEY=SUA_CHAVE_DE_LICENCA
```

2. Através de arquivo de configuração (instance/license.json):
```json
{
  "license_key": "SUA_CHAVE_DE_LICENCA"
}
```

## Estrutura do Projeto

```
alphasystem/
├── app/
│   ├── __init__.py
│   ├── config.py
│   ├── models/
│   │   └── __init__.py
│   ├── routes/
│   │   ├── main.py
│   │   ├── auth.py
│   │   ├── products.py
│   │   └── sales.py
│   ├── static/
│   │   ├── css/
│   │   └── js/
│   ├── templates/
│   │   ├── base.html
│   │   ├── index.html
│   │   ├── dashboard.html
│   │   ├── auth/
│   │   ├── products/
│   │   └── sales/
│   └── utils/
│       ├── license_manager.py
│       └── ...
├── run.py
├── requirements.txt
├── .env.example
└── README.md
```

## Configuração de Variáveis de Ambiente

Para configurar o sistema, crie um arquivo `.env` na raiz do projeto com base no arquivo `.env.example`:

```bash
cp .env.example .env
```

Edite o arquivo `.env` com suas credenciais reais:

```env
# .env
SECRET_KEY=sua_chave_secreta_gerada_aqui
DB_USER=seu_usuario_do_banco
DB_PASSWORD=sua_senha_do_banco
DB_HOST=localhost
DB_PORT=3306
DB_NAME=alpha_local
ADMIN_USERNAME=admin
ADMIN_PASSWORD=sua_senha_admin
ADMIN_EMAIL=seu_email_admin@empresa.com
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=seu_email@gmail.com
EMAIL_HOST_PASSWORD=sua_senha_de_app
```

> **Observação:** Se as variáveis `ADMIN_USERNAME`, `ADMIN_PASSWORD` e `ADMIN_EMAIL` não forem definidas, o sistema criará um usuário admin com os valores padrão: `admin`/`admin123`.

### Como gerar uma SECRET_KEY segura:

Execute o seguinte comando no terminal:

```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### Configuração para Recuperação de Senha

Para ativar a funcionalidade de recuperação de senha por email:

1. Preencha as variáveis de email no arquivo `.env`
2. Use uma senha de app com Gmail (não sua senha padrão)
3. Acesse `https://myaccount.google.com/`, vá em "Segurança" e gere uma "Senha de app"
4. A senha de app deve ter 16 caracteres (ex: `abcd efgh ijkl mnop`)

### Verificação da Configuração

Para verificar se seu arquivo `.env` está configurado corretamente:

```bash
python check_env.py
```

## Funcionamento do Sistema de Licenças

O sistema implementa um mecanismo de controle de licenças com as seguintes características:

- A licença é validada online a cada 30 dias
- Se a validação online falhar, o sistema permite uso por até 3 dias extras
- Caso a licença esteja expirada ou inválida, o acesso ao sistema é bloqueado
- O servidor central para validação de licenças deve ser implementado separadamente

## Personalização

O sistema pode ser facilmente adaptado para diferentes clientes:

- Interfaces podem ser personalizadas nos arquivos HTML em `app/templates/`
- Lógica de negócios pode ser modificada em `app/routes/`
- Modelos de dados podem ser estendidos em `app/models/`
- Estilos podem ser modificados em `app/static/css/`

## Desenvolvimento

Para desenvolvimento, o sistema pode ser executado em modo debug:

```bash
export FLASK_ENV=development
python run.py
```

## Novo Controle de Caixa

O sistema agora inclui um controle de caixa moderno com as seguintes funcionalidades:

### Para todos os usuários:
- Abertura e fechamento de caixa com controle de saldo
- Registro automático das vendas no caixa ativo
- Controle de despesas
- Visualização de transações (vendas, despesas, entradas e saídas)
- Histórico de caixas
- Integração completa com o dashboard

### Para gerentes e administradores:
- Visão geral de todos os caixas abertos dos usuários gerenciados
- Resumo das vendas do dia por usuário
- Receita total do dia para todos os usuários gerenciados
- Dashboard gerencial com informações consolidadas
- Acompanhamento em tempo real do status dos caixas dos subordinados

## Implantação

### Em produção tradicional

Para implantação em produção tradicional, recomenda-se:

- Configurar um servidor WSGI como Gunicorn ou uWSGI
- Colocar o sistema atrás de um proxy reverso como Nginx
- Configurar variáveis de ambiente apropriadamente
- Configurar o banco de dados para produção
- Implementar o servidor central para validação de licenças

### No Vercel com MySQL e Ngrok

O Alphasystem pode ser implantado no Vercel com MySQL, usando ngrok para expor o banco de dados local. O arquivo `vercel.json` já está configurado para isso.

#### Configuração no Vercel:

1. Faça fork deste repositório no GitHub
2. Importe o projeto no Vercel
3. Configure as variáveis de ambiente conforme abaixo
4. O deploy será feito automaticamente

#### Variáveis de ambiente necessárias:

As mesmas variáveis definidas no arquivo `.env` devem ser configuradas como variáveis de ambiente no Vercel:

- `SECRET_KEY`: Chave secreta para a aplicação Flask
- `LOCAL_DB_USER`: Usuário do banco de dados local
- `LOCAL_DB_PASSWORD`: Senha do banco de dados local
- `LOCAL_DB_HOST`: Host do banco de dados local (para acesso remoto do Vercel, ex: xxx.ngrok.io)
- `LOCAL_DB_PORT`: Porta do banco de dados local
- `LOCAL_DB_NAME`: Nome do banco de dados local
- `ONLINE_DB_USER`: Usuário do banco de dados online (para validação de licenças)
- `ONLINE_DB_PASSWORD`: Senha do banco de dados online
- `ONLINE_DB_HOST`: Host do banco de dados online
- `ONLINE_DB_PORT`: Porta do banco de dados online
- `ONLINE_DB_NAME`: Nome do banco de dados online
- `ADMIN_USERNAME`: Nome de usuário para o admin (opcional)
- `ADMIN_PASSWORD`: Senha para o admin (opcional)
- `ADMIN_EMAIL`: Email para o admin (opcional)
- `EMAIL_HOST`: Servidor SMTP para envio de emails
- `EMAIL_PORT`: Porta do servidor SMTP
- `EMAIL_HOST_USER`: Usuário do email
- `EMAIL_HOST_PASSWORD`: Senha do email ou senha de app
- `PRATELEIRA_LICENSE_KEY`: Chave de licença (opcional)

> **Importante sobre o banco de dados local:** O Vercel está hospedando apenas o aplicativo Flask, não o banco de dados. Para o banco de dados local com MySQL, você tem as seguintes opções:
>
> 1. **Expor seu banco de dados MySQL local via túnel ngrok** para acesso remoto (abordagem descrita neste guia)
> 2. **Utilizar um banco de dados MySQL hospedado** (ex: AWS RDS, Google Cloud SQL, PlanetScale, etc.)
> 3. **Mover o banco de dados local para um provedor externo MySQL** e ajustar as variáveis de ambiente
>
> Em qualquer caso, o `LOCAL_DB_HOST`, `LOCAL_DB_USER`, `LOCAL_DB_PASSWORD`, etc. devem apontar para onde seu banco de dados local está hospedado e acessível via internet.

#### Usando Ngrok para Expor o Banco de Dados MySQL:

Para usar ngrok para expor seu banco de dados MySQL local para o ambiente do Vercel:

1. **Instale o ngrok** em sua máquina local
2. **Configure seu MySQL para aceitar conexões remotas** (veja documentação em `docs/ngrok_mysql_setup.md`)
3. **Crie um usuário MySQL com acesso remoto**:
   ```sql
   CREATE USER 'seu_usuario'@'%' IDENTIFIED BY 'sua_senha_segura';
   GRANT ALL PRIVILEGES ON alpha_local.* TO 'seu_usuario'@'%';
   FLUSH PRIVILEGES;
   ```
4. **Inicie o túnel ngrok para o MySQL**:
   ```bash
   ngrok tcp 3306
   ```
5. **Use o host e porta fornecidos pelo ngrok** como os valores para `LOCAL_DB_HOST` e `LOCAL_DB_PORT` no Vercel

> **Atenção à segurança:** Ao expor seu banco de dados local via ngrok, certifique-se de usar senhas fortes e monitore o acesso ao seu banco de dados.

Para instruções detalhadas sobre a configuração do ngrok com MySQL, consulte `docs/ngrok_mysql_setup.md`.

Para instruções completas de deploy no Vercel, consulte `docs/vercel_deploy_guide.md`.

## Configuração de Múltiplos Bancos de Dados

Este sistema suporta dois bancos de dados MariaDB:

1. **Banco Local**: Armazenamento no cliente (dados operacionais como usuários, produtos, vendas, caixas, etc.)
2. **Banco Online**: Hospedado remotamente, usado exclusivamente para **validação de licenças**

### Estrutura de Configuração

#### Arquivo `.env`
- Variáveis separadas para cada banco de dados (`LOCAL_DB_*` e `ONLINE_DB_*`)
- Configuração simplificada: apenas o `.env` precisa ser alterado por cliente

#### Componentes Implementados
- `app/config.py`: Configuração separada para ambos os bancos
- `app/database_manager.py`: Gerenciamento seguro de múltiplas conexões
- `app/models/__init__.py`: Modelo License atualizado com método de classe para validação online
- `app/utils/license_manager.py`: Sistema de validação de licenças com fallbacks
- `app/routes/licenses.py`: Atualizado para registrar licenças no banco online (em rede local)

### Processo de Validação de Licenças
1. Verificação local da licença
2. A cada 30 dias, validação no banco de dados online
3. Se validação online falhar, período de carência de 3 dias
4. Após carência, acesso negado até validação bem sucedida

## Sincronização de Licenças (Ambiente de Produção vs Rede Local)

### Em ambiente de produção (servidor online real):
- Licenças válidas são criadas no sistema administrativo central
- As licenças são automaticamente registradas no banco de dados online
- Clientes podem validar suas licenças, mas não criar novas licenças válidas
- Apenas licenças previamente registradas no servidor central são válidas

### Em rede local (para testes):
- As licenças criadas localmente são automaticamente registradas no banco online para testes
- Isso permite simular o comportamento real do sistema
- No script de criação de licenças (`app/routes/licenses.py`), há uma funcionalidade que tenta salvar a licença também no banco online
- Isso é feito apenas para desenvolvimento/testes locais

### Como funcionará em um sistema real:
1. Somente o administrador central pode criar licenças válidas no servidor central
2. As licenças são registradas no banco online e distribuídas para validação
3. Clientes recebem a chave da licença e o sistema valida automaticamente no servidor
4. O processo de validação é transparente para o cliente final

## Funcionalidade de Recuperação de Senha

O sistema inclui uma funcionalidade de recuperação de senha por email:

### Configuração Necessária
- Configurar as variáveis de ambiente de email no arquivo `.env`
- A funcionalidade enviará um email com um link seguro de redefinição de senha
- Os tokens de redefinição expiram após 1 hora por segurança

### Uso da Funcionalidade
1. Na tela de login, clique no link "Esqueceu sua senha?"
2. Informe seu email cadastrado no sistema
3. Acesse seu email e clique no link de redefinição
4. Defina uma nova senha forte e segura

### Requisitos de Segurança
- A nova senha deve atender aos critérios de segurança:
  - Mínimo de 8 caracteres
  - Letras maiúsculas e minúsculas
  - Números
  - Caracteres especiais