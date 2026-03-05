@echo off
title Tesseract Downloader
echo ============================================
echo   Descargando Tesseract OCR para Nova
echo ============================================
echo.

REM Link a SourceForge mirror que suele ser ms permisivo
set "URL=https://digi.bib.uni-mannheim.de/tesseract/tesseract-ocr-w64-setup-5.3.3.20231005.exe"
set "OUT=tools\tesseract_setup.exe"

echo [1/2] Descargando instalador...
powershell -Command "[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; $web = New-Object System.Net.WebClient; $web.Headers.Add('User-Agent', 'Mozilla/5.0'); $web.DownloadFile('%URL%', '%OUT%')"

if exist "%OUT%" (
    echo.
    echo [2/2] ¡Descarga completada!
    echo.
    echo Buscando el archivo en: %OUT%
    echo.
    echo INSTRUCCIONES:
    echo 1. Ejecuta el archivo 'tools\tesseract_setup.exe'
    echo 2. Instala con las opciones por defecto.
    echo 3. ¡Nova ya podrá ver!
) else (
    echo.
    echo [ERROR] No se pudo descargar automáticamente. 
    echo         Por favor, descárgalo manualmente de:
    echo         https://github.com/UB-Mannheim/tesseract/wiki
)

pause
