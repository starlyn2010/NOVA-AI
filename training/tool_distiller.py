import os
import json

class ToolDistiller:
    def __init__(self):
        self.root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.dataset_path = os.path.join(self.root, "knowledge", "datasets", "tool_traces.json")
        
    def generate_traces(self):
        traces = [
            {
                "intent": "autonomous_project_management",
                "prompt": "Crea un plan de marketing en Notion, busca imágenes de referencia en Pixazo para cada punto y crea tareas en Trello para el diseñador.",
                "chain": [
                    {"tool": "notion", "action": "create structured marketing plan doc"},
                    {"tool": "pixazo", "action": "generate 5 distinct visual prompts based on plan sections"},
                    {"tool": "trello", "action": "create board 'Marketing' with cards for each visual task"}
                ],
                "logic": "Descomposición jerárquica. El Plan es el origen. Trello es la ejecución. Pixazo es el asset."
            },
            {
                "intent": "audio_visual_summary",
                "prompt": "Descarga este video de YouTube, saca el audio, resume lo que dice en Notion y súbelo a mi Drive.",
                "chain": [
                    {"tool": "youtube", "action": "download mp4 / extract mp3"},
                    {"tool": "audio", "action": "transcribe via Whisper (Local)"},
                    {"tool": "notion", "action": "save summary in knowledge base"},
                    {"tool": "google_drive", "action": "upload summary.txt and audio.mp3"}
                ]
            }
        ]
        with open(self.dataset_path, "w", encoding="utf-8") as f:
            json.dump(traces, f, indent=4, ensure_ascii=False)
        print(f"Trazas de herramientas destiladas en {self.dataset_path}")

if __name__ == "__main__":
    distiller = ToolDistiller()
    distiller.generate_traces()
