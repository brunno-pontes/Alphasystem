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

```bash
# Crie um banco de dados chamado 'prateleira_db'
# Atualize as variáveis de ambiente conforme necessário:
export DB_USER=seu_usuario
export DB_PASSWORD=sua_senha
export DB_HOST=localhost
export DB_PORT=3306
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
└── README.md
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