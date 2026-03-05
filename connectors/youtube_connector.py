"""
Nova YouTube Connector — Production v2.8.0
============================================
Download, transcribe, and analyze YouTube videos using yt-dlp.
No API key required — fully local and free.
"""

import os
import subprocess
import json
import re
from .base import BaseConnector


class YouTubeConnector(BaseConnector):
    NAME = "youtube"
    REQUIRED_KEYS = []  # No API keys — uses yt-dlp

    def __init__(self):
        super().__init__()
        self._root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self._downloads_dir = os.path.join(self._root, "data", "youtube_downloads")
        os.makedirs(self._downloads_dir, exist_ok=True)
        self._ytdlp = self._find_ytdlp()

    def _find_ytdlp(self) -> str:
        """Locate yt-dlp binary."""
        venv_path = os.path.join(self._root, "venv", "Scripts", "yt-dlp.exe")
        if os.path.exists(venv_path):
            return venv_path
        # Try system PATH
        try:
            result = subprocess.run(
                ["yt-dlp", "--version"],
                capture_output=True, text=True, timeout=5,
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0,
            )
            if result.returncode == 0:
                return "yt-dlp"
        except Exception:
            pass
        return ""

    def health_check(self) -> dict:
        if self._ytdlp:
            return self._ok("YouTube connector listo (yt-dlp disponible).")
        return self._warn(
            "yt-dlp no encontrado. Instala con: pip install yt-dlp",
            instructions_for_llm="yt-dlp no está instalado. El usuario debe ejecutar: pip install yt-dlp",
        )

    def get_info(self, url: str) -> dict:
        """Get video metadata without downloading."""
        if not self._ytdlp:
            return self._err("yt-dlp no instalado. Ejecuta: pip install yt-dlp")

        try:
            result = subprocess.run(
                [self._ytdlp, "--dump-json", "--no-download", url],
                capture_output=True, text=True, timeout=30,
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0,
            )
            if result.returncode != 0:
                return self._err(f"Error obteniendo info: {result.stderr}")

            info = json.loads(result.stdout)
            return self._ok(
                f"Info del video: {info.get('title', 'Sin título')}",
                title=info.get("title"),
                channel=info.get("channel"),
                duration=info.get("duration"),
                duration_string=info.get("duration_string"),
                view_count=info.get("view_count"),
                upload_date=info.get("upload_date"),
                description=info.get("description", "")[:500],
                thumbnail=info.get("thumbnail"),
                url=url,
                instructions_for_llm=(
                    f"Video: '{info.get('title')}' — Canal: {info.get('channel')} — "
                    f"Duración: {info.get('duration_string')} — Vistas: {info.get('view_count', 'N/A')}"
                ),
            )
        except Exception as e:
            return self._err(f"Error: {e}")

    def download_video(self, url: str, quality: str = "best[height<=720]") -> dict:
        """Download a video."""
        if not self._ytdlp:
            return self._err("yt-dlp no instalado.")

        try:
            output_template = os.path.join(self._downloads_dir, "%(title)s.%(ext)s")
            result = subprocess.run(
                [
                    self._ytdlp,
                    "-f", quality,
                    "-o", output_template,
                    "--no-playlist",
                    "--limit-rate", "5M",
                    url,
                ],
                capture_output=True, text=True, timeout=300,
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0,
            )
            if result.returncode == 0:
                # Find the downloaded file
                lines = result.stdout.split("\n")
                filepath = ""
                for line in lines:
                    if "Destination:" in line:
                        filepath = line.split("Destination:")[-1].strip()
                    elif "has already been downloaded" in line:
                        filepath = line.split("[download]")[-1].split("has already")[0].strip()

                return self._ok(
                    f"Video descargado exitosamente.",
                    filepath=filepath or self._downloads_dir,
                    url=url,
                )
            return self._err(f"Error descargando: {result.stderr}")
        except subprocess.TimeoutExpired:
            return self._err("Timeout: la descarga tardó demasiado.")
        except Exception as e:
            return self._err(f"Error: {e}")

    def download_audio(self, url: str) -> dict:
        """Download only the audio track (MP3)."""
        if not self._ytdlp:
            return self._err("yt-dlp no instalado.")

        try:
            output_template = os.path.join(self._downloads_dir, "%(title)s.%(ext)s")
            result = subprocess.run(
                [
                    self._ytdlp,
                    "-x", "--audio-format", "mp3",
                    "-o", output_template,
                    "--no-playlist",
                    url,
                ],
                capture_output=True, text=True, timeout=300,
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0,
            )
            if result.returncode == 0:
                return self._ok("Audio extraído en MP3.", url=url)
            return self._err(f"Error: {result.stderr}")
        except Exception as e:
            return self._err(f"Error: {e}")

    def get_subtitles(self, url: str, lang: str = "es") -> dict:
        """Download subtitles/transcript."""
        if not self._ytdlp:
            return self._err("yt-dlp no instalado.")

        try:
            output_template = os.path.join(self._downloads_dir, "%(title)s")
            result = subprocess.run(
                [
                    self._ytdlp,
                    "--write-auto-sub",
                    "--sub-lang", lang,
                    "--skip-download",
                    "--convert-subs", "srt",
                    "-o", output_template,
                    url,
                ],
                capture_output=True, text=True, timeout=60,
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0,
            )
            if result.returncode == 0:
                return self._ok("Subtítulos descargados.", url=url, lang=lang)
            return self._err(f"Error: {result.stderr}")
        except Exception as e:
            return self._err(f"Error: {e}")

    # ── Unified Contract ────────────────────────────────────────────
    def _execute(self, request: str) -> dict:
        req = request.strip().lower()

        # Extract URL from request
        url_match = re.search(r'(https?://[^\s]+)', request)
        url = url_match.group(1) if url_match else ""

        if not url:
            return self._warn(
                "Proporciona una URL de YouTube. Ejemplo: descargar https://youtube.com/watch?v=...",
                instructions_for_llm="Pide al usuario que proporcione la URL del video de YouTube.",
            )

        if "audio" in req or "mp3" in req or "música" in req:
            return self.download_audio(url)
        if "subtítulo" in req or "subtitulo" in req or "transcript" in req:
            return self.get_subtitles(url)
        if "info" in req or "datos" in req:
            return self.get_info(url)
        if "descargar" in req or "download" in req or "bajar" in req:
            return self.download_video(url)

        # Default: get info
        return self.get_info(url)
