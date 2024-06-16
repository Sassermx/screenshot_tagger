@echo off
setlocal

:: Cambia al directorio del script
cd /d "%~dp0"

:: Instala Python 3.9 si no está instalado
python --version 2>NUL
if %ERRORLEVEL% NEQ 0 (
    echo Python no está instalado. Descargando e instalando Python 3.9...
    powershell -Command "Start-Process msiexec.exe -ArgumentList '/i https://www.python.org/ftp/python/3.9.0/python-3.9.0-amd64.exe /quiet InstallAllUsers=1 PrependPath=1' -NoNewWindow -Wait"
)

:: Instala los paquetes requeridos
echo Instalando paquetes necesarios...
python -m pip install -r ../requirements.txt

:: Llama la ejecución del archivo Python main.py
echo Ejecutando main.py...
python ../main.py

:end
