# Nova - Advanced AI Agent

Nova is a local-first autonomous agent with Level 5 intent routing, semantic memory (RAG), and modular engines.

## Key Features
- Level 5 Routing: hybrid N-Grams + LLM fallback.
- Semantic Memory: TF-IDF context retrieval.
- Multi-Engine: files, vision, visuals, programming, search, tools, security.
- Local LLM: GGUF model with `llama-cpp-python` (no Ollama required).

## Setup (No Ollama)
1. Create/prepare environment with `setup_nova.bat`.
2. This script installs `requirements-core.txt`, `llama-cpp-python` and downloads a GGUF model into `models/`.
3. On older CPUs, Nova can fallback automatically to `ctransformers`.
4. Start Nova with `start.bat`.

## Optional Modules
- Audio: `pip install -r requirements-audio.txt`
- Web crawling: `pip install -r requirements-web.txt`
- Extra engines: `pip install -r requirements-extra.txt`
- Math: `pip install -r requirements-math.txt`

## Security
Nova includes protection against:
- Path traversal in file operations.
- Unauthorized script execution outside allowed folders.
- Risk pattern checks in SecurityShield.

## License
MIT. See `LICENSE`.
