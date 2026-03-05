import os
import sys
import time
from pathlib import Path

import requests


DEFAULT_URL = (
    "https://huggingface.co/TheBloke/TinyLlama-1.1B-Chat-v1.0-GGUF/resolve/main/"
    "tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf?download=true"
)
DEFAULT_NAME = "tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf"


def human_bytes(n: int) -> str:
    units = ["B", "KB", "MB", "GB", "TB"]
    size = float(max(0, n))
    for u in units:
        if size < 1024 or u == units[-1]:
            return f"{size:.2f} {u}"
        size /= 1024
    return f"{n} B"


def download_file(url: str, dest: Path, timeout: int = 60) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    part = dest.with_suffix(dest.suffix + ".part")

    downloaded = part.stat().st_size if part.exists() else 0
    headers = {"Range": f"bytes={downloaded}-"} if downloaded > 0 else {}

    with requests.get(url, stream=True, timeout=timeout, headers=headers, allow_redirects=True) as r:
        r.raise_for_status()

        total_header = r.headers.get("Content-Length")
        total = int(total_header) + downloaded if total_header and downloaded else int(total_header or 0)

        mode = "ab" if downloaded > 0 else "wb"
        with open(part, mode) as f:
            t0 = time.time()
            last_print = 0.0
            for chunk in r.iter_content(chunk_size=1024 * 1024):
                if not chunk:
                    continue
                f.write(chunk)
                downloaded += len(chunk)

                now = time.time()
                if now - last_print >= 1.0:
                    speed = downloaded / max(now - t0, 1e-6)
                    if total > 0:
                        pct = (downloaded / total) * 100
                        print(
                            f"[DOWNLOAD] {pct:6.2f}% | {human_bytes(downloaded)}/{human_bytes(total)} | {human_bytes(int(speed))}/s",
                            flush=True,
                        )
                    else:
                        print(
                            f"[DOWNLOAD] {human_bytes(downloaded)} | {human_bytes(int(speed))}/s",
                            flush=True,
                        )
                    last_print = now

    part.replace(dest)


def main() -> int:
    project_root = Path(__file__).resolve().parents[1]
    models_dir = project_root / "models"
    url = os.getenv("NOVA_GGUF_URL", DEFAULT_URL).strip()
    filename = os.getenv("NOVA_GGUF_NAME", DEFAULT_NAME).strip()
    dest = models_dir / filename

    if dest.exists() and dest.stat().st_size > 50 * 1024 * 1024:
        print(f"[OK] Modelo ya existe: {dest}")
        print(f"[OK] Tamano: {human_bytes(dest.stat().st_size)}")
        return 0

    print(f"[INFO] Descargando modelo GGUF a: {dest}")
    print(f"[INFO] URL: {url}")
    try:
        download_file(url, dest)
    except Exception as e:
        print(f"[ERROR] No se pudo descargar el modelo: {e}")
        return 1

    if not dest.exists() or dest.stat().st_size < 50 * 1024 * 1024:
        print("[ERROR] Descarga incompleta o archivo invalido.")
        return 1

    print(f"[OK] Modelo descargado: {dest}")
    print(f"[OK] Tamano final: {human_bytes(dest.stat().st_size)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
