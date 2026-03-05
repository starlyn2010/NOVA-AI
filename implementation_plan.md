# Plan de Estabilización Final: Nova v2.7.1 (Optimización 8GB) 🛡️⚙️💎

Este parche asegura que Nova sea ligera, estable y coherente, optimizada para equipos con 8GB de RAM.

## Ajustes Finales de Seguridad
1. **Rollback Manual**: Dado que no se detectó un repositorio Git, se realizará un respaldo manual en `backups/v2.7.0/` de todos los archivos modificados antes de proceder.
2. **Sincronización de Intents**: Los nombres en `signals.yaml` coincidirán exactamente con `orchestrator.py` (`crawl`, `watchdog`, `shield`, `audio`, `comm`, `maintenance`, `wiki`, `ui`).
3. **Umbral de Rendimiento**: Límite de incremento de RAM en **400MB** y tiempo de arranque en **< 2 segundos**.

## Contrato Unificado de Motores
Todos los motores en `orchestrator.py` deben cumplir con `process(input: str) -> dict`.

| Motor | Intent Signal | Input Esperado | Salida Esperada |
| :--- | :--- | :--- | :--- |
| **AudioEngine** | `audio` | Query/Ruta | `status`, `transcription` |
| **CommEngine** | `comm` | Texto | `status`, `message`, `target` |
| **WikiGenerator** | `wiki` | Texto/Título | `status`, `wiki_path`, `message` |
| **SecurityShield**| `shield` | Ruta archivo | `status`, `risk_level`, `patterns`, `score` |
| **WebCrawler** | `crawl` | URL | `status`, `content`, `title` |

## Proposed Changes

### [Core] [orchestrator.py](file:///C:/Users/DELL/Desktop/inventos/Nova/orchestrator.py)
- Estandarizar la llamada a `process(current_input)`.

### [Router] [signals.yaml](file:///C:/Users/DELL/Desktop/inventos/Nova/core/router/signals.yaml)
- Añadir intents con pesos: `audio` (0.85), `crawl` (0.90), `watchdog` (0.95), `shield` (0.95), `comm` (0.80), `maintenance` (0.80), `wiki` (0.85), `ui` (0.70).

### [Engines] Lazy Loading Estricto
- **[AudioEngine](file:///C:/Users/DELL/Desktop/inventos/Nova/engines/audio/audio_engine.py)**: Mover `import whisper` al método `process`.
- **[WebCrawler](file:///C:/Users/DELL/Desktop/inventos/Nova/engines/search/web_crawler_engine.py)**: Mover `playwright` al método `process` + Check de binarios.
- **[MathEngine](file:///C:/Users/DELL/Desktop/inventos/Nova/engines/mathematics/math_engine.py)**: Mover `sympy` al método `process`.
- **[VisualEngine](file:///C:/Users/DELL/Desktop/inventos/Nova/engines/visuals/visual_engine.py)**: Mover `matplotlib` al método `process`.
- **[KnowledgeIngestor](file:///C:/Users/DELL/Desktop/inventos/Nova/engines/knowledge/ingestor_engine.py)**: Mover `pdfplumber` y `docx` a sus respectivos métodos de extracción.

### [Build] Módulos de Requisitos
- **requirements-core.txt**: Base (YAML, requests, etc.).
- **requirements-extra.txt**: numpy, matplotlib, pillow, etc.
- **requirements-math.txt**: sympy.
- **requirements-audio.txt**: openai-whisper.
- **requirements-web.txt**: playwright.

## Verification Plan
1. **Startup Performance**: `tools/verify_performance.py` (Debe ser < 2 segundos el arranque base).
2. **RAM Test**: `tools/verify_ram.py` (< 400MB de incremento en reposo).
3. **Cache Integrity Test**: Validar que `%USERPROFILE%\.cache\whisper` y `%LOCALAPPDATA%\ms-playwright` no cambien durante el arranque.

## Plan de Rollback
- Criterio: RAM > 400MB o Startup > 2s.
- Acción: Restaurar archivos desde `backups/v2.7.0/` usando un script de recuperación.
