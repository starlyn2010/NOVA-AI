import re
import os

class SecurityShield:
    """
    Escudo de Seguridad de Nova: Escanea archivos en busca de 
    patrones maliciosos, scripts ocultos y macros peligrosas.
    """
    def __init__(self):
        # Patrones comunes de malware/scripts peligrosos
        self.malicious_patterns = [
            r"eval\(", r"exec\(", r"os\.system\(", r"subprocess\.Popen", 
            r"powershell -e", r"base64\.b64decode", r"shutil\.rmtree",
            r"\\.exe", r"\\.dll", r"\\.bat", r"\\.sh", r"\\.vbs"
        ]

    def scan_file(self, file_path: str) -> dict:
        """Escanea un archivo y devuelve el nivel de riesgo. Seguro contra KeyErrors."""
        res = {
            "status": "success",
            "risk_level": "LOW",
            "patterns_found": [],
            "risk_score": 0,
            "message": ""
        }

        if not file_path or not os.path.exists(file_path):
            res["status"] = "error"
            res["risk_level"] = "UNKNOWN"
            res["message"] = f"Archivo no encontrado: {file_path}"
            return res

        risk_score = 0
        matching_patterns = []

        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
                for pattern in self.malicious_patterns:
                    if re.search(pattern, content, re.IGNORECASE):
                        risk_score += 1
                        matching_patterns.append(pattern)
        except Exception as e:
            res["status"] = "error"
            res["message"] = str(e)
            return res

        if risk_score > 3:
            res["risk_level"] = "HIGH"
        elif risk_score > 0:
            res["risk_level"] = "MEDIUM"

        res["risk_score"] = risk_score
        res["patterns_found"] = matching_patterns
        return res

    def process(self, file_path: str, health_check: bool = False) -> dict:
        """Interfaz unificada para el Orchestrator."""
        if health_check:
            return {"status": "success", "message": "SecurityShield ready."}
            
        if not file_path or not os.path.isfile(file_path):
            return {
                "status": "success",
                "risk_level": "N/A",
                "patterns_found": [],
                "risk_score": 0,
                "message": "Envíe una ruta de archivo válida para escanear."
            }

        scan_res = self.scan_file(file_path)
        
        report = f"REPORTE DE SEGURIDAD PARA: {os.path.basename(file_path)}\n"
        report += f"Nivel de Riesgo: {scan_res['risk_level']}\n"
        if scan_res['patterns_found']:
            report += f"Filtros disparados: {', '.join(scan_res['patterns_found'])}\n"
            
        return {
            "status": scan_res["status"],
            "security_report": report,
            "risk_level": scan_res['risk_level'],
            "patterns": scan_res["patterns_found"],
            "score": scan_res["risk_score"],
            "instructions_for_llm": f"Informa al usuario sobre la seguridad del archivo:\n{report}"
        }
