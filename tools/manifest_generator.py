
import json
import os
import hashlib
from datetime import datetime

class ManifestGenerator:
    """
    Generador de Manifiesto Industrial: Registra los entregables y asegura trazabilidad.
    """
    def __init__(self, output_dir="deliverables"):
        self.output_dir = output_dir
        self.manifest_path = os.path.join(output_dir, "manifest.json")
        os.makedirs(output_dir, exist_ok=True)
        self.files = {}

    def _calculate_hash(self, filepath):
        hasher = hashlib.sha256()
        try:
            with open(filepath, 'rb') as f:
                while chunk := f.read(4096):
                    hasher.update(chunk)
            return hasher.hexdigest()
        except Exception:
            return "n/a"

    def register_file(self, filepath, description, category="code"):
        if not os.path.exists(filepath):
            return
            
        rel_path = os.path.relpath(filepath, os.getcwd())
        self.files[rel_path] = {
            "description": description,
            "category": category,
            "timestamp": datetime.now().isoformat(),
            "sha256": self._calculate_hash(filepath)
        }

    def generate(self):
        data = {
            "project": "Nova Industrial v3.0",
            "generation_date": datetime.now().isoformat(),
            "status": "Production Ready",
            "deliverables": self.files
        }
        with open(self.manifest_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        print(f"--- Manifiesto generado en {self.manifest_path} ---")

if __name__ == "__main__":
    # Registro de archivos clave de esta sesion
    gen = ManifestGenerator()
    gen.register_file(".env.example", "Plantilla de variables de entorno", "security")
    gen.register_file("core/security/env_loader.py", "Cargador central de secretos", "security")
    gen.register_file("knowledge/datasets/logic_core.json", "Dataset optimizado y sanitizado", "knowledge")
    gen.register_file("tools/regression_suite.py", "Suite de pruebas industriales", "qa")
    gen.register_file("tools/stress_monitor.py", "Monitor de recursos RAM/CPU", "qa")
    gen.register_file("tools/audio_diag.py", "Diagnostico de hardware de audio", "troubleshooting")
    gen.generate()
