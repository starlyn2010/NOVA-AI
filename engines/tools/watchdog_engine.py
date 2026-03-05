import psutil
import platform
import os
from datetime import datetime

class WatchdogSystem:
    """
    Sistema Watchdog de Nova: Monitorea el rendimiento del PC,
    temperaturas y procesos sospechosos.
    """
    def __init__(self):
        self.history = []

    def get_system_health(self) -> dict:
        """Obtiene un resumen del estado de salud del sistema."""
        cpu_usage = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        health = {
            "timestamp": datetime.now().isoformat(),
            "cpu_usage_percent": cpu_usage,
            "memory_usage_percent": memory.percent,
            "memory_available_gb": round(memory.available / (1024**3), 2),
            "disk_usage_percent": disk.percent,
            "os": platform.system(),
            "architecture": platform.machine()
        }
        
        # Alertas críticas
        alerts = []
        if cpu_usage > 90:
            alerts.append("CRÍTICO: El uso de CPU es extremadamente alto.")
        if memory.percent > 90:
            alerts.append("CRÍTICO: La memoria RAM está casi agotada.")
        if disk.percent > 95:
            alerts.append("PELIGRO: El disco principal está casi lleno.")
            
        health["alerts"] = alerts
        return health

    def get_top_processes(self, n=5) -> list:
        """Devuelve los N procesos que más recursos consumen."""
        processes = []
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
            try:
                processes.append(proc.info)
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
        
        # Ordenar por uso de CPU
        top_cpu = sorted(processes, key=lambda x: x['cpu_percent'], reverse=True)[:n]
        return top_cpu

    def process(self, request: str, health_check: bool = False) -> dict:
        """Interfaz para el Orchestrator."""
        if health_check:
            return {"status": "success", "message": "WatchdogSystem ready."}

        if os.getenv("NOVA_TEST_MODE", "").strip().lower() in {"1", "true", "mock"}:
            report = (
                "SALUD DEL SISTEMA (MOCK):\n"
                "- CPU: 12%\n"
                "- RAM: 48% (3.90 GB libres)\n"
                "- DISCO: 65%\n"
            )
            return {
                "status": "success",
                "health_report": report,
                "top_processes": [],
                "instructions_for_llm": f"Informa al usuario sobre el estado de su PC basÃ¡ndote en este reporte:\n{report}"
            }
             
        health = self.get_system_health()
        top_procs = self.get_top_processes()
        
        report = f"SALUD DEL SISTEMA ({health['os']}):\n"
        report += f"- CPU: {health['cpu_usage_percent']}%\n"
        report += f"- RAM: {health['memory_usage_percent']}% ({health['memory_available_gb']} GB libres)\n"
        report += f"- DISCO: {health['disk_usage_percent']}%\n"
        
        if health["alerts"]:
            report += "\n⚠️ ALERTAS ACTIVAS:\n" + "\n".join(health["alerts"])
            
        return {
            "status": "success",
            "health_report": report,
            "top_processes": top_procs,
            "instructions_for_llm": f"Informa al usuario sobre el estado de su PC basándote en este reporte:\n{report}"
        }
