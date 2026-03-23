import json
import os
from datetime import datetime, timedelta

class CompactionEngine:
    """
    Motor de Compactación de Memoria: Resume logs antiguos
    para mantener el contexto relevante sin saturar el sistema.
    """
    def __init__(self, logs_path=None):
        self.base_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        if logs_path is None:
            self.logs_path = os.path.join(self.base_path, "logs")
        else:
            self.logs_path = logs_path

    def get_old_logs(self, days=7):
        """Busca logs más antiguos que N días."""
        old_logs = []
        cutoff = datetime.now() - timedelta(days=days)
        
        if not os.path.exists(self.logs_path):
            return []
            
        for file in os.listdir(self.logs_path):
            if file.endswith(".log"):
                file_path = os.path.join(self.logs_path, file)
                mtime = datetime.fromtimestamp(os.path.getmtime(file_path))
                if mtime < cutoff:
                    old_logs.append(file_path)
        return old_logs

    def compact_memory(self):
        """
        Simula la compactación: En un sistema LLM real, enviaría los logs 
        antiguos a un modelo para generar un resumen 'semántico' y luego borraría los archivos.
        """
        old_logs = self.get_old_logs()
        if not old_logs:
            return "No hay memorias lo suficientemente antiguas para compactar."
            
        print(f"[Compaction] Compactando {len(old_logs)} archivos de log...")
        # Lógica de resumen (Placeholder para integración con Integrator)
        summary = f"RESUMEN SEMÁNTICO - {datetime.now().strftime('%Y-%m-%d')}\n"
        summary += f"Compactados logs de {len(old_logs)} sesiones de actividad."
        
        # Guardar resumen en la memoria persistente
        memory_file = os.path.join(self.base_path, "data", "compacted_memory.txt")
        os.makedirs(os.path.dirname(memory_file), exist_ok=True)
        with open(memory_file, "a", encoding="utf-8") as f:
            f.write(summary + "\n")
            
        # Limpieza (Para propósitos de seguridad, solo renombramos en vez de borrar de golpe)
        for log in old_logs:
            os.rename(log, log + ".compacted")
            
        return f"Éxito: Se han archivado {len(old_logs)} memorias antiguas."

    def process(self, request: str, health_check: bool = False) -> dict:
        """Interfaz para el Orchestrator."""
        if health_check:
            return {"status": "success", "message": "CompactionEngine ready."}

        if os.getenv("NOVA_TEST_MODE", "").strip().lower() in {"1", "true", "mock"}:
            res = "Modo prueba: compactacion simulada sin cambios en disco."
            return {
                "status": "success",
                "message": res,
                "instructions_for_llm": f"Informa al usuario sobre el mantenimiento de memoria: {res}"
            }
             
        res = self.compact_memory()
        return {
            "status": "success",
            "message": res,
            "instructions_for_llm": f"Informa al usuario sobre el mantenimiento de memoria: {res}"
        }
