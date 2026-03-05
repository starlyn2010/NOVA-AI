"""
Nova Telegram Connector — Production v2.8.0
=============================================
Full duplex: send messages AND listen for incoming commands.
The bot runs in a background thread so Nova stays responsive.
"""

import threading
import time
from .base import BaseConnector


class TelegramConnector(BaseConnector):
    NAME = "telegram"
    REQUIRED_KEYS = ["bot_token", "chat_id"]

    def __init__(self):
        super().__init__()
        self._updater = None
        self._listener_thread = None
        self._running = False
        self._callback = None  # function(text) called when a message arrives

    # ── Core API ────────────────────────────────────────────────────
    def send(self, text: str, chat_id: str = None) -> dict:
        """Send a message to a Telegram chat."""
        token = self._cfg("bot_token")
        target = chat_id or self._cfg("chat_id")
        if not token or not target:
            return self._warn("Telegram no configurado. Añade bot_token y chat_id en config.yaml → connectors → telegram")

        try:
            import requests
            url = f"https://api.telegram.org/bot{token}/sendMessage"
            payload = {"chat_id": target, "text": text, "parse_mode": "Markdown"}
            r = requests.post(url, json=payload, timeout=10)
            r.raise_for_status()
            return self._ok("Mensaje enviado por Telegram.", chat_id=target)
        except Exception as e:
            return self._err(f"Error enviando Telegram: {e}")

    def get_updates(self, offset: int = None) -> list:
        """Fetch new messages from the bot."""
        token = self._cfg("bot_token")
        if not token:
            return []
        try:
            import requests
            url = f"https://api.telegram.org/bot{token}/getUpdates"
            params = {"timeout": 30, "allowed_updates": ["message"]}
            if offset:
                params["offset"] = offset
            r = requests.get(url, params=params, timeout=35)
            r.raise_for_status()
            return r.json().get("result", [])
        except Exception:
            return []

    # ── Listener (Background Thread) ────────────────────────────────
    def start_listening(self, callback):
        """Start long-polling in background. callback(text, chat_id) is called for each message."""
        if self._running:
            return
        self._callback = callback
        self._running = True
        self._listener_thread = threading.Thread(target=self._poll_loop, daemon=True)
        self._listener_thread.start()
        print("[Telegram] Listener activo — esperando mensajes remotos.")

    def stop_listening(self):
        self._running = False

    def _poll_loop(self):
        offset = None
        while self._running:
            try:
                updates = self.get_updates(offset)
                for u in updates:
                    offset = u["update_id"] + 1
                    msg = u.get("message", {})
                    text = msg.get("text", "")
                    chat_id = msg.get("chat", {}).get("id")
                    if text and self._callback:
                        self._callback(text, str(chat_id))
            except Exception as e:
                print(f"[Telegram] Polling error: {e}")
                time.sleep(5)

    # ── Unified Contract ────────────────────────────────────────────
    def _execute(self, request: str) -> dict:
        return self.send(request)
