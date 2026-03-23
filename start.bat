@echo off
title Nova v2.8.0 - OLLAMA POWER BRAIN
echo ============================================
echo   Nova v2.8.0 - MODO INTELIGENCIA SUPERIOR
echo ============================================
echo.

REM 1. Set working directory to script location
cd /d "%~dp0"

REM 2. Check virtual environment
if not exist "venv\Scripts\python.exe" (
    echo [ERROR] No se encuentra el entorno virtual.
    echo         Ejecuta: python -m venv venv
    pause
    exit /b 1
)

REM 3. Check for Ollama Service
echo [STATUS] Verificando conexion con Ollama...
curl -s http://localhost:11434/api/tags > nul
if errorlevel 1 (
    echo [WARNING] Ollama no parece estar corriendo. 
    echo           Asegurate de abrir Ollama para usar el Cerebro Potente.
    echo.
)

REM 4. Launch Nova UI
echo [OK] Lanzando Nova...
start "Nova v2.8.0" venv\Scripts\pythonw.exe ui\main.py
exit
