# Manual Tecnico de Operacion Nova (8GB)

## 1. Objetivo
Este manual define instalacion, operacion, seguridad y recuperacion para Nova en equipos limitados a 8GB RAM.

## 2. Instalacion Base
1. Crear entorno virtual: `python -m venv venv`
2. Activar entorno: `venv\Scripts\activate`
3. Instalar base: `pip install -r requirements.txt`
4. Verificar: `python tools/smoke_test_engines.py`

## 3. Perfil de Recursos
- Objetivo de arranque: < 2s
- Incremento RAM en reposo: < 400MB
- Sin descargas automaticas en inicio

## 4. Operacion Diaria
1. Iniciar Nova
2. Validar estado de motores
3. Ejecutar tarea principal
4. Registrar hallazgos en wiki
5. Cerrar con verificacion rapida

## 5. Troubleshooting
- Si responde lento: revisar modelo activo y timeout.
- Si repite respuestas genericas: validar integrador y backend local GGUF.
- Si falla un motor: ejecutar smoke test y revisar `raw_status`.

## 6. Seguridad
- Permitir scripts solo en carpetas autorizadas.
- Mantener lista de patrones de riesgo en SecurityShield.
- Evitar rutas fuera del proyecto (path traversal).

## 7. Backup y Rollback
1. Respaldar `config.yaml`, `orchestrator.py`, `core/`, `engines/`.
2. Guardar snapshot de `data/`.
3. Revertir solo archivos afectados por incidente.

## 8. Checklist de Release
- Smoke 17/17 PASS
- Performance PASS
- RAM PASS
- No-download PASS
- Documentacion actualizada
