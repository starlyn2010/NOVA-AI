from core.llm.ollama_client import OllamaClient
import yaml
import os

class Supervisor:
    def __init__(self):
        # Load config to get model names
        config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "config.yaml")
        with open(config_path, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)
             
        llm_cfg = config.get("llm", {})
        self.supervisor_model = llm_cfg.get("supervisor_model", "local-gguf")
        self.request_timeout = int(llm_cfg.get("timeout", 30))
        self.test_mode = os.getenv("NOVA_TEST_MODE", "").strip().lower() in {"1", "true", "mock"}
        self.client = OllamaClient(default_model=self.supervisor_model, request_timeout=self.request_timeout)
        
        self.system_prompt = """ERES EL SUPERVISOR LÓGICO DE UNA IA.
Tu trabajo es decidir si el usuario quiere CONTINUAR con la tarea actual o CAMBIAR a una nueva.

INPUT:
- Tarea Actual: [La tarea que se estaba haciendo]
- Último Input Usuario: [Lo que el usuario acaba de decir]

SALIDA ESPERADA:
Responde SOLO con una de estas dos palabras:
- CONTINUE (Si el usuario quiere modificar, corregir, ampliar o seguir con la tarea actual)
- CHANGE (Si el usuario quiere cambiar radicalmente de tema, empezar algo nuevo o abandonar la tarea actual)

EJEMPLOS:
Tarea: Programación | Input: "Cambia el color a rojo" -> CONTINUE
Tarea: Programación | Input: "Ahora cuéntame un chiste" -> CHANGE
Tarea: Creativo | Input: "Haz que el dragón sea azul" -> CONTINUE
Tarea: Creativo | Input: "Escribe un script en python" -> CHANGE
Tarea: Programación | Input: "No, eso está mal" -> CONTINUE
"""

    def _heuristic_decision(self, user_input: str) -> str:
        text = (user_input or "").lower().strip()
        if not text:
            return "CHANGE"

        continue_markers = [
            "ajusta", "corrige", "mejora", "continua", "continúa",
            "sigue", "hazlo", "cambia ", "modifica", "expande", "amplia", "amplía",
        ]
        change_markers = [
            "nuevo tema", "otra cosa", "cambia de tema", "olvida eso",
            "ahora quiero", "ahora dime", "hablemos de", "pasemos a",
        ]

        if any(m in text for m in change_markers):
            return "CHANGE"
        if any(m in text for m in continue_markers):
            return "CONTINUE"
        return "UNKNOWN"

    def decide(self, current_intent: str, user_input: str) -> str:
        if not current_intent or current_intent == "social":
            return "CHANGE" # Conversational or empty context always open to change

        # Fast path: avoid expensive LLM call when possible.
        heuristic = self._heuristic_decision(user_input)
        if heuristic in {"CONTINUE", "CHANGE"}:
            return heuristic

        if self.test_mode:
            return "CHANGE"
             
        prompt = f"Tarea Actual: {current_intent.upper()}\nÚltimo Input Usuario: {user_input}\nDECISIÓN:"
        
        try:
            response = self.client.generate(
                prompt=prompt, 
                system=self.system_prompt, 
                model=self.supervisor_model,
                stream=False
            )
            
            decision = response.get("response", "").strip().upper()
            
            # Cleanup output just in case
            if "CONTINUE" in decision: return "CONTINUE"
            if "CHANGE" in decision: return "CHANGE"
            
            return "CHANGE" # Default to change if unsure
            
        except Exception as e:
            print(f"Supervisor Error: {e}")
            return "CHANGE" # Fallback
