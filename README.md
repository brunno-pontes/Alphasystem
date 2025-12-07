# Sistema Prateleira

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
cd sistema_prateleira
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

Agora, crie o banco de dados e o usuário conforme especificado na configuração:

```bash
# Conecte-se ao MariaDB como root
sudo mysql -u root

# Dentro do console do MariaDB, execute:
ALTER USER 'root'@'localhost' IDENTIFIED BY 'Rootbr@10!';
CREATE DATABASE IF NOT EXISTS `alpha-db`;
GRANT ALL PRIVILEGES ON `alpha-db`.* TO 'root'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

Se você encontrar o erro "Access denied for user 'root'@'localhost'" ou "Column 'authentication_string' is not updatable", use os comandos apropriados para sua versão do MariaDB:

```bash
# Conecte-se ao MariaDB como root
sudo mysql -u root

# Dentro do console do MariaDB, execute os comandos apropriados para sua versão:

# Para versões mais recentes do MariaDB:
ALTER USER 'root'@'localhost' IDENTIFIED BY 'Rootbr@10!';
CREATE DATABASE IF NOT EXISTS `alpha-db`;
GRANT ALL PRIVILEGES ON `alpha-db`.* TO 'root'@'localhost';
FLUSH PRIVILEGES;

# Para versões mais antigas do MariaDB/MySQL (se ALTER USER não funcionar):
USE mysql;
UPDATE user SET authentication_string = PASSWORD('Rootbr@10!') WHERE User = 'root' AND Host = 'localhost';
FLUSH PRIVILEGES;
CREATE DATABASE IF NOT EXISTS `alpha-db`;
GRANT ALL PRIVILEGES ON `alpha-db`.* TO 'root'@'localhost';
FLUSH PRIVILEGES;

EXIT;
```

5. Execute o sistema:

```bash
python run.py
```

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
sistema_prateleira/
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
DB_USER=root
DB_PASSWORD=root
DB_HOST=localhost
DB_PORT=3306
DB_NAME=alpha-db
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=seu_email@gmail.com
EMAIL_HOST_PASSWORD=sua_senha_de_app
```

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

Para implantação em produção, recomenda-se:

- Configurar um servidor WSGI como Gunicorn ou uWSGI
- Colocar o sistema atrás de um proxy reverso como Nginx
- Configurar variáveis de ambiente apropriadamente
- Configurar o banco de dados para produção
- Implementar o servidor central para validação de licenças

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