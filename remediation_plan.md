# Plan de Remediación Crítica: Fase 22 (Nivel OpenAI) 🛡️🛠️

Este plan aborda los 15 hallazgos de la auditoría de Codex para elevar a Nova de "prototipo" a "nivel de producto".

## Bloque 0: Emergencia (P0 - Fixes Inmediatos) [Hallazgos 1, 2, 4]
1. **Sintaxis en `integrator.py`:** Reparar el bloque `try/except`.
2. **Engine Mismatch:** Renombrar `process_query` a `process` en `VisualEngine` para restaurar visualizaciones.
3. **Safety Clean:** Eliminar/Sanitizar contenido de autolesión en `conocimiento_nova.json`.

## Bloque 1: Seguridad y Blindaje (P1 - Alta Severidad) [Hallazgos 3, 5, 14]
1. **Path Traversal:** Implementación de `os.path.commonpath` en `FileEngine`.
2. **Script Allowlist:** Crear una lista blanca de rutas permitidas para ejecución en el `Orchestrator`.
3. **Tesseract Fix:** Corregir el bat de descarga y verificar hashes/urls.

## Bloque 2: Inteligencia y Estabilidad (P1/P2) [Hallazgos 6, 7, 8, 9, 10]
1. **Prompt Optimizer:** Implementar carga dinámica de skills (solo inyectar las necesarias) para evitar el "bloat".
2. **Persistencia Sólida:** Unificar el formato de guardado de `MemoryEngine` y `SemanticMemory`.
3. **Robustez de Red:** Añadir timeouts a todas las peticiones de `ollama_client.py`.
4. **Environment Check:** Fix automático de dependencias faltantes y nombres de modelos.

## Bloque 3: Calidad de Ingeniería (P3) [Hallazgos 11, 12, 13, 15]
1. **Refactor de Orchestrator:** Eliminar ejecuciones dobles.
2. **Profile Sync:** Unificar esquema de nombres (`nombre` vs `name`).
3. **Supervisor Integration:** Hacer que el supervisor realmente tome decisiones o eliminarlo.
4. **Professional Docs:** Crear el README, .gitignore y LICENSE oficiales.

---
> [!IMPORTANT]
> Responderé a tus preguntas de auditoría:
> 1. **Target:** Seguiremos enfocados en **Local/Offline**, lo que hace que la seguridad de archivos sea vital para que Nova no dañe el sistema del usuario accidentalmente.
> 2. **Tools Action:** Implementaremos una **Allowlist** estricta. Ningún script fuera de carpetas autorizadas se ejecutará.
> 3. **Fases:** Ya he activado la Fase 22 en el mapa.
