@echo off
title Nova Setup (Local GGUF)
echo ============================================
echo   Configurando Nova v2.8.0 (Sin Ollama)
echo ============================================
echo.

REM 1. Ensure working directory
cd /d "%~dp0"

REM 2. Ensure virtual environment
if not exist "venv\Scripts\python.exe" (
    echo [INFO] Creando entorno virtual...
    python -m venv venv
    if %ERRORLEVEL% NEQ 0 (
        echo [ERROR] No se pudo crear el entorno virtual.
        pause
        exit /b 1
    )
)

REM 3. Upgrade pip and install core dependencies
venv\Scripts\python.exe -m pip install --upgrade pip
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Fallo actualizando pip.
    pause
    exit /b 1
)

echo [INFO] Instalando dependencias base (llama-cpp incluido)...
venv\Scripts\python.exe -m pip install llama-cpp-python==0.3.2 --extra-index-url https://abetlen.github.io/llama-cpp-python/whl/cpu
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Fallo instalando llama-cpp-python wheel CPU precompilado.
    pause
    exit /b 1
)

venv\Scripts\python.exe -m pip install -r requirements-core.txt
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Fallo instalando requirements-core.txt
    pause
    exit /b 1
)

REM 4. Download local GGUF model
echo [INFO] Descargando modelo GGUF local...
venv\Scripts\python.exe tools\setup_local_model.py
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Fallo al descargar el modelo GGUF.
    pause
    exit /b 1
)

echo.
echo [EXITO] Nova lista en modo local GGUF (sin Ollama).
echo Ejecuta start.bat para iniciar la interfaz.
echo.
pause
