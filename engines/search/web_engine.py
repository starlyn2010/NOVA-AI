import os
try:
    from duckduckgo_search import DDGS
except ImportError:
    from ddgs import DDGS

class WebSearchEngine:
    """
    Motor de búsqueda web ligero usando DuckDuckGo.
    Devuelve fragmentos de texto relevantes para enriquecer el contexto.
    """
    def __init__(self):
        pass

    def search(self, query: str, max_results: int = 3) -> str:
        """
        Realiza una búsqueda y devuelve un resumen formateado.
        """
        print(f"DEBUG: Buscando en web: '{query}'")
        try:
            with DDGS() as ddgs:
                results = list(ddgs.text(query, max_results=max_results))
            
            if not results:
                return "No se encontraron resultados en la web."
            
            summary = [f"--- Resultados de búsqueda para: '{query}' ---"]
            for i, r in enumerate(results, 1):
                title = r.get('title', 'Sin título')
                body = r.get('body', '')
                href = r.get('href', '')
                summary.append(f"[{i}] {title}\n    {body}\n    Fuente: {href}")
            
            return "\n".join(summary)
            
        except Exception as e:
            return f"Error en búsqueda web: {str(e)}"

    def process(self, query: str, health_check: bool = False) -> dict:
        """
        Interfaz estándar para el Orchestrator.
        """
        if health_check:
            return {"status": "success", "message": "WebSearchEngine ready."}

        if os.getenv("NOVA_TEST_MODE", "").strip().lower() in {"1", "true", "mock"}:
            return {
                "status": "success",
                "web_results": f"[MockSearch] Resultado simulado para: {query}",
                "instructions_for_llm": f"Usa este resultado simulado para responder: {query}",
            }
             
        result_text = self.search(query)
        return {
            "status": "success",
            "web_results": result_text,
            "instructions_for_llm": f"Usa esta información de internet para responder:\n{result_text}"
        }
