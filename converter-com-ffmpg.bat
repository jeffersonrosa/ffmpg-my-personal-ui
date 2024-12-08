@echo off
if not exist ".venv" (
    echo Criando ambiente virtual...
    python -m venv .venv
    if %ERRORLEVEL% neq 0 (
        echo Erro ao criar ambiente virtual. Certifique-se que o Python está instalado e no PATH.
        pause
        goto end
    )
    call .venv\Scripts\activate
    echo Instalando dependencias...
    pip install -r requirements.txt
) else (
    call .venv\Scripts\activate
)

python main.py

:end
