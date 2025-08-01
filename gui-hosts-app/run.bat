@echo off
cd /d "%~dp0"
echo 🛡️ Iniciando Hosts Generator...
echo.
pip install -r requirements.txt
python main.py

if errorlevel 1 (
    echo.
    echo ❌ Error al ejecutar la aplicación.
    echo.
    echo Posibles soluciones:
    echo 1. Instalar dependencias: pip install -r requirements.txt
    echo 2. Verificar que Python esté instalado
    echo.
    pause
)