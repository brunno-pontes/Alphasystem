@echo off
echo Iniciando o Sistema Prateleira...

REM Verificar se o ambiente virtual está ativo
if not defined VIRTUAL_ENV (
    echo Ativando ambiente virtual...
    call venv\Scripts\activate.bat
)

REM Instalar dependências se necessário
if not exist "venv" (
    echo Criando ambiente virtual...
    python -m venv venv
    call venv\Scripts\activate.bat
    pip install -r requirements.txt
) else (
    call venv\Scripts\activate.bat
)

REM Executar o sistema
echo Iniciando o servidor...
python run.py
pause