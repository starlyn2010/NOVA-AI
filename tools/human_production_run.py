import json
import multiprocessing as mp
import os
import re
import sys
import time
from datetime import datetime

sys.path.append(os.getcwd())


def sanitize_filename(name: str, default: str = "output") -> str:
    cleaned = re.sub(r"[^a-zA-Z0-9._-]+", "_", (name or "").strip())
    cleaned = cleaned.strip("._")
    return cleaned or default


def extract_artifacts(text: str):
    pattern = re.compile(
        r'<artifact\s+title="([^"]+)"\s+type="([^"]+)"\s*>(.*?)</artifact>',
        re.DOTALL | re.IGNORECASE,
    )
    return pattern.findall(text or "")


def extract_codeblocks(text: str):
    pattern = re.compile(r"```([a-zA-Z0-9_+-]*)\n(.*?)```", re.DOTALL)
    return pattern.findall(text or "")


def extension_for_lang(lang: str) -> str:
    mapping = {
        "python": ".py",
        "py": ".py",
        "javascript": ".js",
        "js": ".js",
        "typescript": ".ts",
        "ts": ".ts",
        "html": ".html",
        "css": ".css",
        "json": ".json",
        "markdown": ".md",
        "md": ".md",
        "sql": ".sql",
        "bash": ".sh",
        "powershell": ".ps1",
    }
    return mapping.get((lang or "").lower(), ".txt")


def save_big_output(run_dir: str, case_id: str, text: str, min_chars: int = 1000):
    saved_files = []
    if len(text or "") < min_chars:
        return saved_files

    artifacts = extract_artifacts(text)
    if artifacts:
        case_dir = os.path.join(run_dir, case_id)
        os.makedirs(case_dir, exist_ok=True)
        for idx, (title, lang, body) in enumerate(artifacts, 1):
            ext = extension_for_lang(lang)
            filename = sanitize_filename(title, f"{case_id}_{idx}") + ext
            path = os.path.join(case_dir, filename)
            with open(path, "w", encoding="utf-8") as f:
                f.write(body.strip() + "\n")
            saved_files.append(path)
        return saved_files

    blocks = extract_codeblocks(text)
    if blocks:
        case_dir = os.path.join(run_dir, case_id)
        os.makedirs(case_dir, exist_ok=True)
        for idx, (lang, body) in enumerate(blocks, 1):
            ext = extension_for_lang(lang)
            filename = f"{case_id}_code_{idx}{ext}"
            path = os.path.join(case_dir, filename)
            with open(path, "w", encoding="utf-8") as f:
                f.write(body.strip() + "\n")
            saved_files.append(path)

        full_txt = os.path.join(case_dir, f"{case_id}_full_response.md")
        with open(full_txt, "w", encoding="utf-8") as f:
            f.write(text.strip() + "\n")
        saved_files.append(full_txt)
        return saved_files

    case_dir = os.path.join(run_dir, case_id)
    os.makedirs(case_dir, exist_ok=True)
    out = os.path.join(case_dir, f"{case_id}.md")
    with open(out, "w", encoding="utf-8") as f:
        f.write(text.strip() + "\n")
    saved_files.append(out)
    return saved_files


def looks_low_quality_for_big_case(text: str) -> bool:
    t = (text or "").strip().lower()
    if len(t) < 1000:
        return True

    bad_signals = [
        "lo siento",
        "no puedo",
        "no se puede",
        "no pude responder",
        "read timed out",
        "httpconnectionpool",
        "falta",
        "token",
    ]
    return any(s in t for s in bad_signals)


def deterministic_big_fallback(prompt: str) -> str:
    try:
        from core.llm.integrator import NovaIntegrator

        integ = NovaIntegrator()
        txt = integ._deterministic_large_fallback(prompt, "social")
        if txt:
            return txt
    except Exception:
        pass
    return ""


def worker_case(prompt: str, max_turns: int, queue: mp.Queue):
    # Real mode only
    os.environ.pop("NOVA_TEST_MODE", None)
    from orchestrator import Orchestrator

    t0 = time.time()
    nova = Orchestrator()
    forced_model = os.getenv("NOVA_FORCE_MODEL", "local-gguf").strip()
    forced_timeout = int(os.getenv("NOVA_REQ_TIMEOUT", "25"))
    if forced_model:
        nova.chat_model = forced_model
        nova.coding_model = forced_model
        nova.integrator.model = forced_model
        nova.integrator.fallback_model = forced_model
        nova.integrator.client.default_model = forced_model
    nova.integrator.request_timeout = forced_timeout
    nova.integrator.client.request_timeout = forced_timeout
    res = nova.process_request(prompt, max_turns=max_turns)
    dt = time.time() - t0

    text = ""
    raw_status = "n/a"
    if isinstance(res, dict):
        text = str(res.get("text", "") or "")
        raw = res.get("raw", {})
        if isinstance(raw, dict):
            raw_status = raw.get("status", "n/a")

    queue.put(
        {
            "latency_sec": round(dt, 3),
            "text": text,
            "text_len": len(text),
            "raw_status": raw_status,
            "timed_out": False,
        }
    )


def run_case_with_timeout(case_id: str, prompt: str, max_turns: int, timeout_sec: int):
    queue = mp.Queue()
    proc = mp.Process(target=worker_case, args=(prompt, max_turns, queue))
    proc.start()
    proc.join(timeout=timeout_sec)

    if proc.is_alive():
        proc.terminate()
        proc.join(timeout=5)
        return {
            "id": case_id,
            "latency_sec": timeout_sec,
            "text": "",
            "text_len": 0,
            "raw_status": "timeout",
            "timed_out": True,
        }

    if not queue.empty():
        data = queue.get()
        data["id"] = case_id
        return data

    return {
        "id": case_id,
        "latency_sec": 0.0,
        "text": "",
        "text_len": 0,
        "raw_status": "no_output",
        "timed_out": False,
    }


def main():
    mp.freeze_support()

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    root_dir = os.path.join("deliverables", f"human_full_run_{timestamp}")
    big_dir = os.path.join(root_dir, "big_outputs")
    os.makedirs(big_dir, exist_ok=True)

    # Big production prompts (save outputs here).
    big_cases = [
        (
            "bank_app",
            (
                "Crea una app bancaria funcional en un solo archivo app.py con Flask + SQLite. "
                "Incluye registro/login, cuentas, deposito/retiro, transferencias y historial. "
                "Entrega codigo completo ejecutable."
            ),
            420,
        ),
        (
            "novela",
            (
                "Escribe una novela corta cyberpunk en español de 6 capitulos y al menos 1500 palabras, "
                "con dialogos, conflicto central, giro final y cierre."
            ),
            420,
        ),
        (
            "manual_tecnico",
            (
                "Genera un manual tecnico completo para operar Nova en PC de 8GB: instalacion, uso, "
                "troubleshooting, seguridad, backup y rollback, en formato claro y largo."
            ),
            360,
        ),
    ]

    # Human probes for broad capability checks (only save if very large).
    probe_cases = [
        ("probe_search", "Busca 3 fuentes sobre agentes IA y resumelas.", 180),
        ("probe_files", "Lista archivos del proyecto y comenta los mas importantes.", 180),
        ("probe_watchdog", "Como esta mi PC en CPU y RAM ahora?", 180),
        ("probe_shield", "Analiza seguridad del archivo README.md", 180),
        ("probe_wiki", "Documenta este resultado en la wiki del proyecto.", 180),
        ("probe_ui", "Ajusta la interfaz al modo creativo.", 180),
        ("probe_maintenance", "Haz mantenimiento de memoria y logs.", 180),
    ]

    report = {
        "run_dir": root_dir,
        "started_at": datetime.now().isoformat(),
        "big_cases": [],
        "probe_cases": [],
        "saved_files": [],
    }

    print(f"[RUN] Carpeta de salida: {root_dir}", flush=True)

    for case_id, prompt, timeout_sec in big_cases:
        print(f"[RUN] Ejecutando grande: {case_id} (timeout={timeout_sec}s)", flush=True)
        row = run_case_with_timeout(case_id, prompt, max_turns=1, timeout_sec=timeout_sec)
        row["used_fallback"] = False

        if row.get("timed_out") or looks_low_quality_for_big_case(row.get("text", "")):
            fallback_text = deterministic_big_fallback(prompt)
            if fallback_text:
                row["text"] = fallback_text
                row["text_len"] = len(fallback_text)
                row["raw_status"] = "fallback"
                row["timed_out"] = False
                row["used_fallback"] = True

        saved = save_big_output(big_dir, case_id, row["text"], min_chars=1000)
        row["saved_files"] = saved
        report["big_cases"].append(row)
        report["saved_files"].extend(saved)

    for case_id, prompt, timeout_sec in probe_cases:
        print(f"[RUN] Ejecutando probe: {case_id} (timeout={timeout_sec}s)", flush=True)
        row = run_case_with_timeout(case_id, prompt, max_turns=1, timeout_sec=timeout_sec)
        report["probe_cases"].append(row)
        saved = save_big_output(big_dir, case_id, row["text"], min_chars=1800)
        report["saved_files"].extend(saved)

    report["finished_at"] = datetime.now().isoformat()

    with open(os.path.join(root_dir, "report.json"), "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    with open(os.path.join(root_dir, "README.txt"), "w", encoding="utf-8") as f:
        f.write("Run de prueba humana real de Nova\n")
        f.write(f"Carpeta de entregables grandes: {big_dir}\n")
        f.write(f"Archivos guardados: {len(report['saved_files'])}\n")
        for p in report["saved_files"]:
            f.write(f"- {p}\n")

    print("[DONE] Run completado.", flush=True)
    print(f"[DONE] Reporte: {os.path.join(root_dir, 'report.json')}", flush=True)
    print(f"[DONE] Entregables grandes: {big_dir}", flush=True)


if __name__ == "__main__":
    main()
