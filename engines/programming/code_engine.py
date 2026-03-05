import re

class CodeEngine:
    def process(self, request: str, health_check: bool = False) -> dict:
        """
        Analyzes code request and generates a structural draft.
        """
        if health_check:
            return {"status": "success", "message": "CodeEngine ready."}

        lang = self._detect_language(request)
        intent = self._detect_intent(request)
        deps = self._detect_dependencies(request, lang)
        
        # Only provide a stub if we are NOT in generation mode
        # For generation, we want the LLM to start from a clean slate
        draft_code = self._generate_stub(lang, request) if intent != "generation" else ""
        
        return {
            "status": "success",
            "language": lang,
            "intent": intent,
            "dependencies_detected": deps,
            "structure_proposal": f"Script en {lang} para {intent}",
            "draft_code": draft_code,
            "instructions_for_llm": f"ESCRIBE EL CÓDIGO COMPLETO Y FUNCIONAL en {lang}. NO uses placeholders ni comentarios tipo 'tu lógica aquí'. Escribe TODAS las funciones y clases necesarias. Si es un script largo, genéralo entero. Incluye manejo de errores."
        }
        
    def _detect_language(self, text: str) -> str:
        text = text.lower()
        if "python" in text or "py" in text or "pip" in text: return "python"
        if "javascript" in text or "js" in text or "node" in text: return "javascript"
        if "html" in text or "web" in text: return "html"
        if "css" in text or "estilo" in text: return "css"
        if "sql" in text: return "sql"
        if "powershell" in text or "ps1" in text: return "powershell"
        return "python" # Default

    def _detect_intent(self, text: str) -> str:
        text = text.lower()
        if "error" in text or "fix" in text or "arregla" in text: return "debugging"
        if "explica" in text or "qué hace" in text: return "explanation"
        if "optimiza" in text or "mejora" in text: return "optimization"
        return "generation"

    def _detect_dependencies(self, text: str, lang: str) -> list:
        deps = []
        text = text.lower()
        if lang == "python":
            if "request" in text or "api" in text or "http" in text: deps.append("requests")
            if "csv" in text or "excel" in text or "xlsx" in text: deps.append("pandas")
            if "grafic" in text or "plot" in text: deps.append("matplotlib")
            if "juego" in text or "game" in text: deps.append("pygame")
            if "imagen" in text: deps.append("pillow")
        return deps

    def _generate_stub(self, lang: str, text: str) -> str:
        if lang == "python":
            return "#!/usr/bin/env python3\n\ndef main():\n    # Tu lógica aquí\n    pass\n\nif __name__ == '__main__':\n    main()"
        if lang == "javascript":
            return "function main() {\n  // Tu lógica aquí\n}\n\nmain();"
        return f"// Código base para {lang}"
