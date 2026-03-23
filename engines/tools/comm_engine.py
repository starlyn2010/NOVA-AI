import os
import re
import smtplib
from email.mime.text import MIMEText
import requests
import yaml

class CommunicationEngine:
    """
    Motor de Conectividad de Nova: Maneja envíos a Telegram,
    WhatsApp (via Webhook) y Email.
    """
    def __init__(self, config_path="config.yaml"):
        self.project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        self._config = self._load_config(config_path)

        self.telegram_token = self._get_cfg(
            "connectors.telegram.bot_token",
            env_key="NOVA_TELEGRAM_BOT_TOKEN",
            default="",
        )
        self.telegram_chat_id = self._get_cfg(
            "connectors.telegram.chat_id",
            env_key="NOVA_TELEGRAM_CHAT_ID",
            default="",
        )

        self.smtp_server = os.getenv("NOVA_EMAIL_SMTP_SERVER", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("NOVA_EMAIL_SMTP_PORT", "587"))
        self.email_user = os.getenv("NOVA_EMAIL_USER", "")
        self.email_pass = os.getenv("NOVA_EMAIL_PASS", "")

    def _load_config(self, config_path: str) -> dict:
        path = config_path
        if not os.path.isabs(path):
            path = os.path.join(self.project_root, config_path)
        try:
            with open(path, "r", encoding="utf-8") as f:
                return yaml.safe_load(f) or {}
        except Exception:
            return {}

    def _get_cfg(self, path: str, env_key: str = None, default=None):
        if env_key:
            env_val = os.getenv(env_key)
            if env_val:
                return env_val

        node = self._config
        for part in path.split("."):
            if not isinstance(node, dict) or part not in node:
                return default
            node = node.get(part)
        return node if node not in (None, "") else default

    def send_telegram(self, message: str) -> bool:
        """Envía un mensaje a Telegram."""
        if not self.telegram_token or not self.telegram_chat_id:
            print("[Comm] Error: Telegram no configurado.")
            return False
            
        url = f"https://api.telegram.org/bot{self.telegram_token}/sendMessage"
        payload = {"chat_id": self.telegram_chat_id, "text": message}
        try:
            response = requests.post(url, json=payload, timeout=10)
            return response.status_code == 200
        except Exception as e:
            print(f"[Comm] Error enviando a Telegram: {e}")
            return False

    def send_email(self, subject: str, body: str, to_email: str) -> bool:
        """Envía un correo electrónico."""
        if not self.email_user or not self.email_pass:
            print("[Comm] Error: Credenciales de email no configuradas.")
            return False
        if not to_email:
            print("[Comm] Error: Destinatario de email no especificado.")
            return False

        msg = MIMEText(body)
        msg['Subject'] = subject
        msg['From'] = self.email_user
        msg['To'] = to_email

        try:
            with smtplib.SMTP(self.smtp_server, self.smtp_port, timeout=10) as server:
                server.starttls()
                server.login(self.email_user, self.email_pass)
                server.send_message(msg)
            return True
        except Exception as e:
            print(f"[Comm] Error enviando email: {e}")
            return False

    def process(self, request: str, health_check: bool = False) -> dict:
        """Interfaz unificada para el Orchestrator."""
        if health_check:
            return {"status": "success", "message": "CommEngine ready."}

        has_telegram_cfg = bool(self.telegram_token and self.telegram_chat_id)
        has_email_cfg = bool(self.email_user and self.email_pass)

        # Si el prompt no contiene datos específicos, pedimos aclaración
        if not request or len(request) < 5:
             return {
                "status": "success",
                "message": "Esperando contenido para enviar vía Telegram o Email.",
                "target": "none"
            }

        # Lógica simple de detección de target en el string
        target = "telegram"
        if "email" in request.lower() or "correo" in request.lower():
            target = "email"
            
        content = request # Usamos el input como contenido por defecto

        # Safe default for unconfigured environments: do not hard-fail.
        if (target == "telegram" and not has_telegram_cfg) or (target == "email" and not has_email_cfg):
            return {
                "status": "success",
                "message": f"Modo simulación: {target} no configurado. Mensaje preparado pero no enviado.",
                "target": target,
                "instructions_for_llm": (
                    f"Indica al usuario que el mensaje para {target} quedó preparado, "
                    "pero faltan credenciales para el envío real."
                ),
            }
        
        # Simulación de envío
        success = False
        if target == "telegram":
            success = self.send_telegram(content)
        elif target == "email":
            # Extraer email destino del mensaje o usar variable de entorno
            match = re.search(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", request)
            to_email = match.group(0) if match else os.getenv("NOVA_EMAIL_TO", "")
            if not to_email:
                return {
                    "status": "success",
                    "message": "Falta el destinatario del email. Indica un correo en el mensaje.",
                    "target": "email",
                }
            success = self.send_email("Aviso de Nova", content, to_email)
            
        return {
            "status": "success" if success else "error",
            "message": "Mensaje enviado" if success else "Error al enviar (Configure credenciales)",
            "target": target,
            "instructions_for_llm": f"Confirma al usuario que el mensaje {target} fue {'enviado' if success else 'fallido'}."
        }
