import os
import json
from datetime import datetime

class WikiGenerator:
    """
    Generador de Wiki Nova: Crea documentación automática para los 
    proyectos que Nova analiza o desarrolla.
    """
    def __init__(self, wiki_path="data/wiki"):
        self.wiki_path = wiki_path
        os.makedirs(self.wiki_path, exist_ok=True)

    def generate_entry(self, project_name: str, analysis_data: str) -> str:
        """Crea o actualiza una entrada en la Wiki para un proyecto."""
        filename = f"{project_name.lower().replace(' ', '_')}.md"
        file_path = os.path.join(self.wiki_path, filename)
        
        content = f"# Proyecto: {project_name}\n"
        content += f"*Última actualización: {datetime.now().strftime('%Y-%m-%d %H:%M')}*\n\n"
        content += "## Resumen del Proyecto\n"
        content += analysis_data + "\n\n"
        content += "---\n*Documentación generada automáticamente por Nova v2.7.0*\n"
        
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
            return file_path
        except Exception as e:
            return f"Error generando Wiki: {e}"

    def process(self, request: str, health_check: bool = False) -> dict:
        """Interfaz unificada para el Orchestrator."""
        if health_check:
            return {"status": "success", "message": "WikiGenerator ready."}
            
        if not request or len(request) < 5:
            return {
                "status": "success",
                "message": "Motor de Wiki listo. Describa el proyecto para documentar.",
                "wiki_path": ""
            }

        # Intentar extraer un nombre de proyecto del texto o usar genérico
        project_name = "Proyecto_Actual"
        res_path = self.generate_entry(project_name, request)
        success = not res_path.startswith("Error")
        
        return {
            "status": "success" if success else "failed",
            "wiki_path": res_path,
            "message": f"Wiki actualizada en {res_path}" if success else res_path,
            "instructions_for_llm": f"Informa al usuario que he actualizado la Wiki en: {res_path}"
        }
