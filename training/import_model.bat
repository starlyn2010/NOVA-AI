@echo off
title Nova - Importador de Modelo Fine-Tuned
echo ============================================
echo   Nova v2.7.0 - Importar Modelo Entrenado
echo ============================================
echo.

REM 1. Verificar que el archivo GGUF existe
set GGUF_PATH_1=%~dp0deepseek-coder-1.3b-instruct.Q4_K_M.gguf
set GGUF_PATH_2=%~dp0unsloth.Q4_K_M.gguf

if exist "%GGUF_PATH_1%" (
    set GGUF_PATH=%GGUF_PATH_1%
) else if exist "%GGUF_PATH_2%" (
    set GGUF_PATH=%GGUF_PATH_2%
) else (
    echo [ERROR] No se encontro el archivo GGUF.
    echo         Asegurate de poner el archivo descargado de Colab
    echo         en esta carpeta: %~dp0
    echo.
    echo         Nombres buscados:
    echo          - deepseek-coder-1.3b-instruct.Q4_K_M.gguf
    echo          - unsloth.Q4_K_M.gguf
    pause
    exit /b 1
)

echo [OK] Archivo GGUF encontrado: %GGUF_PATH%
echo.

REM 2. Crear Modelfile temporal apuntando al GGUF
echo [INFO] Creando configuracion de modelo...

(
echo FROM %GGUF_PATH%
echo.
echo SYSTEM """Eres Nova, una IA asistente experta y amigable creada por Starlyn.
echo.
echo REGLAS:
echo 1. Responde SIEMPRE en espanol.
echo 2. Para codigo completo usa: ^<artifact title="nombre" type="lenguaje"^>...^</artifact^>
echo 3. Genera codigo COMPLETO, nunca stubs.
echo 4. Se breve en charla, exhaustiva en tecnica."""
echo.
echo PARAMETER temperature 0.5
echo PARAMETER num_ctx 2048
echo PARAMETER top_p 0.9
echo PARAMETER repeat_penalty 1.1
) > "%~dp0Modelfile_finetuned"

echo [OK] Configuracion creada.
echo.

REM 3. Crear modelo en Ollama
echo [INFO] Importando modelo a Ollama (esto puede tardar unos minutos)...
ollama create nova-finetuned -f "%~dp0Modelfile_finetuned"

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ============================================
    echo   EXITO! Modelo 'nova-finetuned' creado
    echo ============================================
    echo.
    echo Para usarlo, actualiza config.yaml:
    echo   default_model: "nova-finetuned"
    echo   coding_model: "nova-finetuned"
    echo   chat_model: "nova-finetuned"
    echo.
    echo O pruebalo directamente:
    echo   ollama run nova-finetuned
    echo.
) else (
    echo.
    echo [ERROR] Fallo al crear el modelo en Ollama.
    echo         Verifica que Ollama este corriendo.
)

pause
