"""
Nova WhatsApp Connector — Production v2.8.0
=============================================
Uses Playwright to automate WhatsApp Web.
After the first QR scan, sessions persist via browser storage.
"""

import os
import json
from .base import BaseConnector


class WhatsAppConnector(BaseConnector):
    NAME = "whatsapp"
    REQUIRED_KEYS = []  # No API keys needed — uses browser automation

    def __init__(self):
        super().__init__()
        self._root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self._session_dir = os.path.join(self._root, "data", "whatsapp_session")
        os.makedirs(self._session_dir, exist_ok=True)

    def health_check(self) -> dict:
        try:
            from playwright.sync_api import sync_playwright
            return self._ok("WhatsApp connector listo (Playwright disponible).")
        except ImportError:
            return self._err("Playwright no instalado. Ejecuta: pip install playwright && playwright install chromium")

    def send_message(self, phone: str, message: str, headless: bool = False) -> dict:
        """
        Send a WhatsApp message via WhatsApp Web.
        First-time use: opens visible browser for QR scan.
        Subsequent uses: reuses saved session (headless capable).
        """
        try:
            from playwright.sync_api import sync_playwright
        except ImportError:
            return self._err("Playwright no instalado.")

        # Normalize phone number
        phone = phone.strip().replace(" ", "").replace("-", "")
        if not phone.startswith("+"):
            phone = f"+{phone}"

        try:
            with sync_playwright() as p:
                browser = p.chromium.launch_persistent_context(
                    user_data_dir=self._session_dir,
                    headless=headless,
                    args=["--disable-blink-features=AutomationControlled"],
                )
                page = browser.pages[0] if browser.pages else browser.new_page()

                # Navigate to WhatsApp Web with pre-filled phone
                encoded_msg = message.replace(" ", "%20")
                url = f"https://web.whatsapp.com/send?phone={phone}&text={encoded_msg}"
                page.goto(url, wait_until="domcontentloaded", timeout=60000)

                # Wait for the message input to appear (means we're logged in)
                try:
                    page.wait_for_selector('[data-tab="10"]', timeout=90000)
                except Exception:
                    # If we timeout, the user probably needs to scan QR
                    return self._warn(
                        "Debes escanear el código QR en el navegador que se abrió. "
                        "Después de escanearlo, vuelve a intentar enviar el mensaje.",
                        action="scan_qr",
                    )

                # Click send button
                import time
                time.sleep(2)
                send_btn = page.query_selector('[data-testid="send"]')
                if send_btn:
                    send_btn.click()
                    time.sleep(3)
                    browser.close()
                    return self._ok(f"Mensaje enviado a {phone} por WhatsApp.", phone=phone)
                else:
                    # Fallback: press Enter
                    page.keyboard.press("Enter")
                    time.sleep(3)
                    browser.close()
                    return self._ok(f"Mensaje enviado a {phone} por WhatsApp (Enter).", phone=phone)

        except Exception as e:
            return self._err(f"Error WhatsApp: {e}")

    def open_session(self) -> dict:
        """Open WhatsApp Web for QR scan (first-time setup)."""
        try:
            from playwright.sync_api import sync_playwright
        except ImportError:
            return self._err("Playwright no instalado.")

        try:
            with sync_playwright() as p:
                browser = p.chromium.launch_persistent_context(
                    user_data_dir=self._session_dir,
                    headless=False,
                )
                page = browser.pages[0] if browser.pages else browser.new_page()
                page.goto("https://web.whatsapp.com", wait_until="domcontentloaded")

                # Wait for user to scan QR and chats to load
                page.wait_for_selector('[data-tab="3"]', timeout=120000)
                browser.close()
                return self._ok("Sesión de WhatsApp guardada correctamente.")
        except Exception as e:
            return self._err(f"Error abriendo WhatsApp: {e}")

    # ── Unified Contract ────────────────────────────────────────────
    def _execute(self, request: str) -> dict:
        """Parse request like 'enviar +34600... Hola mundo'"""
        parts = request.strip().split(None, 1)
        if len(parts) < 2:
            return self._warn(
                "Formato: <número_teléfono> <mensaje>. Ejemplo: +34600123456 Hola, te escribo desde Nova."
            )
        phone, message = parts[0], parts[1]
        return self.send_message(phone, message)
