
import os
import sys
import json
import time

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

try:
    from core.llm.integrator import NovaIntegrator
    from orchestrator import Orchestrator
except ImportError as e:
    print(f"[ERROR] No se pudo importar el núcleo de Nova: {e}")
    sys.exit(1)

class NovaMirror:
    def __init__(self):
        self.orchestrator = Orchestrator()
        self.history = []
        print("[BRIDGE] Puente Antigravity-Nova Activo.")

    def chat_with_nova(self, prompt, is_voice=False):
        print(f"\n[ANTIGRAVITY]: {prompt}")
        print("[NOVA PENSANDO]...", end="", flush=True)
        
        start_time = time.time()
        response = self.orchestrator.process_request(prompt, is_voice=is_voice)
        elapsed = time.time() - start_time
        
        text = response.get("text", "")
        # Detect fallback
        is_mock = "[MOCK MODE" in text
        is_templated = "artifact" in text.lower() and ("app_banco_flask" in text or "Manual Tecnico" in text)
        
        print(f"\r[NOVA] ({elapsed:.2f}s) | Calidad: {'TEMPLATED' if is_templated else 'LLM REAL' if not is_mock else 'MOCK'}")
        print("-" * 50)
        print(text)
        print("-" * 50)
        
        return text

    def run_diagnostic_loop(self):
        prompts = [
            "Hola Nova, soy Antigravity. Estoy auditando tu cerebro. ¿Quien eres exactamente y cual es tu protocolo de fallo?",
            "Necesito un script en Python que analice la frecuencia de palabras en un log, pero no uses ninguna libreria externa.",
            "Explícame cómo funciona el motor de búsqueda semántica que tienes instalado.",
            "Si el usuario te pide un manual de usuario de Nova, ¿generas uno nuevo o usas uno pre-escrito?",
            "Dame una opinion tecnica sobre el uso de TinyLlama en equipos de 8GB RAM."
        ]
        
        for p in prompts:
            self.chat_with_nova(p)
            time.sleep(1)

if __name__ == "__main__":
    mirror = NovaMirror()
    mirror.run_diagnostic_loop()
