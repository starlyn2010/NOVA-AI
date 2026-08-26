# NOVA — Advanced Local-First AI Agent

[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=flat-square&logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/Core-Orchestrator-009688?style=flat-square)](https://github.com/starlyn2010/NOVA-AI)
[![TypeScript](https://img.shields.io/badge/UI-Tkinter%20%2B%20Web-3178C6?style=flat-square&logo=typescript&logoColor=white)](#)
[![Tailwind CSS](https://img.shields.io/badge/Style-TkinterWeb-06B6D4?style=flat-square&logo=tailwindcss&logoColor=white)](#)
[![MIT License](https://img.shields.io/badge/license-MIT-green?style=flat-square)](LICENSE)

Local-first autonomous agent with **Level 5 intent routing**, **semantic memory (TF-IDF RAG without external DB)**, and **modular engines**. Runs a GGUF LLM via `llama-cpp-python` (no Ollama required) or falls back to `ctransformers` on older CPUs.

> **Honest status:** 463 commits, paused since March 2026. Requires ~8GB RAM for the GGUF model. Streaming architecture (Welford online stats) fits 4.9M-orbit analysis in 380MB RAM. Not a hosted SaaS — local execution by design.

---

## Key features

- **Level 5 routing:** hybrid N-grams + LLM fallback, `sticky_mode` support (`config.yaml`)
- **Semantic memory:** TF-IDF + scikit-learn retrieval, compaction, profile memory, `knowledge/datasets`
- **Multi-engine:** `engines/` + `skills/` (140+ skills), connectors (GitHub, Notion, Telegram, Spotify, VSCode, YouTube, ...), tools, vision, visuals, programming, search
- **Local LLM:** GGUF via `llama-cpp-python`; Ollama backend optional (`config.yaml` `llm.backend: ollama|local`), 4096 context, 2048 max tokens
- **Security:** `SecurityShield` — path-traversal guard, allowed-folder execution, risk-pattern checks

## Project structure

```
NOVA-AI/
├── orchestrator.py              # Central orchestrator (Router → Security → LLM → Memory)
├── config.yaml                  # system, llm, router, paths (version 2.8.0)
├── core/
│   ├── router/                  # intent_router, semantic_router, supervisor, signals.yaml
│   ├── llm/                     # integrator, ollama_client
│   ├── memory/                  # engine, semantic_rag, dynamic_memory, compaction, profile
│   ├── security/                # shield, env_loader
│   ├── knowledge/               # wiki_generator
│   └── skills/loader.py
├── engines/                     # modular engines
├── skills/                      # 140+ skills (agenda_master, api_mocker, autodoc, etc.)
├── connectors/                  # github, notion, spotify, telegram, whatsapp, youtube, etc.
├── tools/                       # verify_*, tesseract, etc.
├── ui/
│   ├── main.py                  # Tkinter UI (main)
│   └── controller.py
├── knowledge/datasets/          # logic_core.json etc.
├── data/                        # chat_history, memory, visuals (gitignored)
├── models/                      # *.gguf (gitignored)
├── requirements-core.txt        # core deps (PyYAML, requests, duckduckgo-search, ctransformers, scikit-learn, numpy, python-dotenv)
├── requirements-audio.txt       # whisper, audio
├── requirements-web.txt         # playwright
├── requirements-extra.txt       # matplotlib, pillow, pytesseract, pdfplumber, etc.
├── requirements-math.txt        # sympy, mpmath, etc.
├── Modelfile / Modelfile.*      # Ollama modelfiles (ultra/light/min)
├── setup_nova.bat / start.bat   # Windows helpers
└── training/
```

## Installation

Prerequisites: Python 3.10+, 8GB RAM recommended, optional Ollama.

```bash
git clone https://github.com/starlyn2010/NOVA-AI.git
cd NOVA-AI

python -m venv venv
# Windows: venv\Scripts\activate
# Linux/macOS: source venv/bin/activate

# core (required)
pip install -r requirements-core.txt
pip install llama-cpp-python  # or ctransformers==0.2.27 for older CPUs (see config.yaml local_runtime: disabled)
# Windows helper does this + downloads GGUF:
# setup_nova.bat
```

Optional modules:

```bash
pip install -r requirements-audio.txt   # audio / whisper
pip install -r requirements-web.txt     # playwright web crawling
pip install -r requirements-extra.txt   # pillow, pytesseract, pdfplumber, python-docx
pip install -r requirements-math.txt    # sympy, mpmath
```

Set up env and config:

```bash
cp .env.example .env   # fill API keys if using connectors; .env is gitignored
# edit config.yaml if you want Ollama:
# llm.backend: ollama
# llm.host: http://localhost:11434
```

Download a GGUF model into `models/` (setup_nova.bat does this) or run via Ollama:

```bash
ollama create nova-ultra -f Modelfile.ultra
ollama run nova-ultra
```

## Scripts / Usage

| Command | Description |
|---------|-------------|
| `python orchestrator.py` | Run orchestrator core (headless) |
| `python ui/main.py` | Start Tkinter UI |
| `python debug_router.py` | Debug intent routing |
| `python pong_test.py` | Connectivity test |
| `python audio_engine.py` | Audio engine test |
| `start.bat` | Windows: start Nova (venv + UI) |
| `setup_nova.bat` | Windows: install deps + download GGUF |

```bash
python orchestrator.py
python ui/main.py
python -m pytest tests/ -q   # if tests present (see remediation_plan.md)
```

`config.yaml` key knobs: `llm.backend`, `llm.host`, `llm.timeout`, `router.min_confidence (0.4)`, `router.use_llm_fallback`, `router.sticky_mode`.

## Deployment / Running locally

Nova is **local-first**, not a cloud deploy:

- **Local:** `python ui/main.py` or `start.bat`. Keep `models/*.gguf` and `data/chat_history.json` local (gitignored).
- **Docker (optional):** wrap `orchestrator.py` + `ui/main.py` if you need containerization; mount `models/` and `data/` as volumes.
- **Connectors:** require `.env` credentials (e.g., `credentials.json` is gitignored). See `connectors/` per-service docs.

No `npm run build` — this is a Python project. CI runs `pip install` + `pytest`.

## Limitations & roadmap

- 8GB RAM minimum for GGUF; older CPUs use `ctransformers` fallback but slower.
- 463 commits, paused March 2026 — contributions welcome but expect gaps.
- `requirements.txt` previously pointed to `requirements-core.txt` via UTF-16 marker — fixed to plain UTF-8.
- See `implementation_plan.md` and `remediation_plan.md` for next phases.

## License

MIT © 2026 Antigravity (Nova Core) / Starlyn. See [LICENSE](LICENSE).

## Citation

See `CITATION.cff`. If you use Nova’s routing or TF-IDF RAG approach, please cite the repo.
