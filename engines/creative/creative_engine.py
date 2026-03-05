import random

class CreativeEngine:
    ARCS = {
        "hero_journey": ["Mundo Ordinario", "Llamada", "Rechazo", "Mentor", "Cruce del Umbral", "Pruebas", "Acercamiento", "Crisis", "Recompensa", "Camino de vuelta", "Resurrección", "Regreso"],
        "three_acts": ["Planteamiento", "Incidente Incitador", "Primer Punto de Giro", "Midpoint", "Segundo Punto de Giro", "Clímax", "Resolución"],
        "mini_story": ["Situación", "Conflicto Inesperado", "Intento de solución", "Giro Final", "Nueva Realidad"]
    }

    THEMES = ["La soledad del poder", "Identidad vs Deber", "Hombre vs Naturaleza", "Tecnología vs Humanidad", "El paso del tiempo"]

    def process(self, request: str, health_check: bool = False) -> dict:
        """
        Generates a rich narrative draft prioritizing 'Show, Don't Tell'.
        """
        if health_check:
            return {"status": "success", "message": "CreativeEngine ready."}
            
        arc_type = "three_acts" # Default
        if "corto" in request.lower() or "micro" in request.lower():
            arc_type = "mini_story"
            
        # Define theme globally for this run
        theme = random.choice(self.THEMES)

        # DETECT COMPLEXITY REQUEST
        complexity = "simple"
        complex_keywords = ["detallada", "larga", "compleja", "novela", "capítulos", "desarrollada"]
        if any(kw in request.lower() for kw in complex_keywords):
            complexity = "complex"

        if complexity == "simple":
            # Better approach: Mini-Structure even for simple stories
            draft = f"SOLICITUD: Escribe una escena sobre: '{request}'.\n"
            draft += f"ESTRUCTURA OBLIGATORIA (Sigue estos pasos):\n"
            draft += "1. INICIO: Empieza con una ACCIÓN concreta o un sonido. (Nada de 'había una vez').\n"
            draft += "2. MEDIO: Debe haber un DIÁLOGO DIRECTO entre personajes. (Usa guiones '- Hola', no digas 'hablaron').\n"
            draft += "3. FINAL: Cierra con una imagen visual o sensorial.\n"
            
            llm_instructions = "Escribe la historia siguiendo la estructura. OBLIGATORIO: Incluye diálogos reales."
            
        else:
            # Full narrative architecture for "escribe una novela de..."
            arc_steps = self.ARCS[arc_type] # theme is already defined above
            draft = f"## ESTRUCTURA DE NOVELA ({arc_type})\n"
            draft += f"**Tema:** {theme}\n"
            draft += "INSTRUCCIONES PARA EL LLM: Escribe escena por escena. NO RESUMAS. USA DIÁLOGOS.\n\n"
            for step in arc_steps:
                draft += f"[{step.upper()}]: {self._generate_beat_prompt(step, request)}\n"
            
            llm_instructions = "Desarrolla la historia completa. PROHIBIDO RESUMIR ('luego hablaron...'). Escribe los diálogos palabra por palabra."

        return {
            "status": "success",
            "arc": arc_type,
            "theme": theme,
            "draft": draft,
            "instructions_for_llm": llm_instructions
        }

    def _generate_beat_prompt(self, step: str, request: str) -> str:
        # Generates a prompt for a specific beat, encouraging specific imagery
        prompts = [
            "Describe el sonido ambiente y la luz, sin decir cómo se siente el personaje.",
            "Inicia con una acción brusca o un diálogo interrumpido.",
            "Céntrate en un objeto pequeño que tenga importancia simbólica.",
            "Usa una metáfora relacionada con el clima para reflejar el estado de ánimo.",
            "Que el silencio diga más que las palabras."
        ]
        return f"[Escribe una escena para '{step}' inspirada en la solicitud. Sugerencia: {random.choice(prompts)}]"
