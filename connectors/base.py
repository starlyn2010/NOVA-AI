"""
Nova Connector Base — Production Framework v2.8.0
==================================================
All connectors inherit from BaseConnector. This ensures:
  - Uniform health_check contract
  - Lazy credential loading from config.yaml
  - Standardised error wrapping
  - Unified logging
"""

import os
import yaml
import datetime


_ENV_LOADED = False


class BaseConnector:
    """Abstract base for every Nova external connector."""

    NAME = "base"
    REQUIRED_KEYS: list = []  # Config keys needed for this connector

    def __init__(self):
        self._ready = False
        self._config = {}
        self._load_config()

    # ── Config ──────────────────────────────────────────────────────
    def _load_config(self):
        root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self._load_env_file(root)
        cfg_path = os.path.join(root, "config.yaml")
        try:
            with open(cfg_path, "r", encoding="utf-8") as f:
                full = yaml.safe_load(f) or {}
            self._config = full.get("connectors", {}).get(self.NAME, {})
        except Exception:
            self._config = {}

    def _cfg(self, key: str, default=None):
        env_key = self._env_key(key)
        env_val = os.getenv(env_key)
        if env_val:
            return env_val

        val = self._config.get(key, default)
        if isinstance(val, str):
            if val.startswith("env:"):
                return os.getenv(val[4:], default)
            if val.startswith("${") and val.endswith("}"):
                return os.getenv(val[2:-1], default)
        return val

    def _load_env_file(self, root: str):
        global _ENV_LOADED
        if _ENV_LOADED:
            return
        env_path = os.path.join(root, ".env")
        if not os.path.exists(env_path):
            _ENV_LOADED = True
            return
        try:
            with open(env_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith("#"):
                        continue
                    if "=" not in line:
                        continue
                    key, value = line.split("=", 1)
                    key = key.strip()
                    value = value.strip().strip('"').strip("'")
                    if key and key not in os.environ:
                        os.environ[key] = value
        finally:
            _ENV_LOADED = True

    def _env_key(self, key: str) -> str:
        def norm(s: str) -> str:
            out = []
            for ch in s.upper():
                out.append(ch if ch.isalnum() else "_")
            return "".join(out)
        return f"NOVA_{norm(self.NAME)}_{norm(key)}"

    # ── Contract ────────────────────────────────────────────────────
    def health_check(self) -> dict:
        missing = [k for k in self.REQUIRED_KEYS if not self._cfg(k)]
        if missing:
            return {
                "status": "warning",
                "message": f"{self.NAME}: faltan credenciales: {', '.join(missing)}",
            }
        return {"status": "success", "message": f"{self.NAME} listo."}

    def process(self, request: str, health_check: bool = False) -> dict:
        if health_check:
            return self.health_check()
        return self._execute(request)

    def _execute(self, request: str) -> dict:
        raise NotImplementedError

    # ── Helpers ─────────────────────────────────────────────────────
    @staticmethod
    def _ts():
        return datetime.datetime.now().isoformat(timespec="seconds")

    @staticmethod
    def _ok(message: str, **extra) -> dict:
        r = {"status": "success", "message": message}
        r.update(extra)
        return r

    @staticmethod
    def _err(message: str, **extra) -> dict:
        r = {"status": "error", "message": message}
        r.update(extra)
        return r

    @staticmethod
    def _warn(message: str, **extra) -> dict:
        r = {"status": "warning", "message": message}
        r.update(extra)
        return r
