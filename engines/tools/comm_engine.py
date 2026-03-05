import smtplib
from email.mime.text import MIMEText
import requests
import json

class CommunicationEngine:
    """
    Motor de Conectividad de Nova: Maneja envíos a Telegram,
    WhatsApp (via Webhook) y Email.
    """
    def __init__(self, config_path="config.yaml"):
        # En un sistema real, esto leería tokens de la configuración
        self.telegram_token = "TU_TOKEN_AQUI"
        self.telegram_chat_id = "TU_CHAT_ID_AQUI"
        self.smtp_server = "smtp.gmail.com"
        self.smtp_port = 587
        self.email_user = "tu_correo@gmail.com"
        self.email_pass = "tu_app_password"

    def send_telegram(self, message: str) -> bool:
        """Envía un mensaje a Telegram."""
        if self.telegram_token == "TU_TOKEN_AQUI":
            print("[Comm] Error: Token de Telegram no configurado.")
            return False
            
        url = f"https://api.telegram.org/bot{self.telegram_token}/sendMessage"
        payload = {"chat_id": self.telegram_chat_id, "text": message}
        try:
            response = requests.post(url, json=payload)
            return response.status_code == 200
        except Exception as e:
            print(f"[Comm] Error enviando a Telegram: {e}")
            return False

    def send_email(self, subject: str, body: str, to_email: str) -> bool:
        """Envía un correo electrónico."""
        if self.email_user == "tu_correo@gmail.com":
            print("[Comm] Error: Credenciales de email no configuradas.")
            return False

        msg = MIMEText(body)
        msg['Subject'] = subject
        msg['From'] = self.email_user
        msg['To'] = to_email

        try:
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
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

        has_telegram_cfg = (
            self.telegram_token != "TU_TOKEN_AQUI"
            and self.telegram_chat_id != "TU_CHAT_ID_AQUI"
        )
        has_email_cfg = (
            self.email_user != "tu_correo@gmail.com"
            and self.email_pass != "tu_app_password"
        )

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
            # Para email real se requerirían más datos, aquí usamos un placeholder
            success = self.send_email("Aviso de Nova", content, "usuario@ejemplo.com")
            
        return {
            "status": "success" if success else "error",
            "message": "Mensaje enviado" if success else "Error al enviar (Configure credenciales)",
            "target": target,
            "instructions_for_llm": f"Confirma al usuario que el mensaje {target} fue {'enviado' if success else 'fallido'}."
        }
