import os
import time

class VisualEngine:
    """
    Motor de visualización para Nova.
    Genera gráficos a partir de datos procesados.
    """
    def __init__(self, output_dir: str = None):
        if output_dir is None:
            self.output_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "data", "visuals")
        else:
            self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

    def generate_chart(self, chart_type: str, labels: list, values: list, title: str = "Resumen de Datos"):
        """
        Genera un archivo .png con un gráfico.
        """
        try:
            import matplotlib.pyplot as plt
            plt.figure(figsize=(10, 6))
            
            if chart_type == "bar":
                plt.bar(labels, values, color="skyblue")
            elif chart_type == "pie":
                plt.pie(values, labels=labels, autopct='%1.1f%%')
            else: # default line
                plt.plot(labels, values, marker='o', linestyle='-', color='orange')
            
            plt.title(title)
            plt.grid(True, linestyle='--', alpha=0.6)
            
            filename = f"chart_{int(time.time())}.png"
            filepath = os.path.join(self.output_dir, filename)
            plt.savefig(filepath)
            plt.close()
            
            return {
                "status": "success",
                "image_path": filepath,
                "relative_path": f"data/visuals/{filename}"
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def process(self, query: str, health_check: bool = False):
        if health_check:
            return {"status": "success", "message": "VisualEngine ready."}
        # Lógica simple para detectar si se pide un gráfico
        if "gráfico" in query.lower() or "visualiza" in query.lower():
            return {
                "status": "success",
                "instructions_for_llm": "El usuario quiere una visualización. Genera una estructura JSON con {type, labels, values, title} para que yo la dibuje."
            }
        return {"status": "success", "message": "Motor visual listo."}
