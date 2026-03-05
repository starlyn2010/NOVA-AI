class UIController:
    """
    Controlador de Interfaz Adaptativa: Genera hooks para que la UI
    cambie de tema o estilo según el contexto.
    """
    def __init__(self):
        self.themes = {
            "coding": {"primary": "#00ff00", "bg": "#1e1e1e", "mode": "dark"},
            "creative": {"primary": "#ff00ff", "bg": "#2e1a47", "mode": "glass"},
            "critical": {"primary": "#ff0000", "bg": "#4a0000", "mode": "alert"},
            "standard": {"primary": "#007acc", "bg": "#f3f3f3", "mode": "light"}
        }

    def get_style_hook(self, intent: str) -> dict:
        """Determina el estilo visual según la intención."""
        if intent in ["programming", "mathematics"]:
            return self.themes["coding"]
        elif intent in ["creative", "social"]:
            return self.themes["creative"]
        elif intent == "watchdog":
            return self.themes["critical"]
        else:
            return self.themes["standard"]

    def process(self, intent: str, health_check: bool = False) -> dict:
        if health_check:
            return {"status": "success", "message": "UIController ready."}
            
        """Interfaz para el Orchestrator."""
        style = self.get_style_hook(intent)
        return {
            "status": "success",
            "ui_adjustment": style,
            "instructions_for_llm": f"Menciona sutilmente que has adaptado tu interfaz para el modo {intent}."
        }
