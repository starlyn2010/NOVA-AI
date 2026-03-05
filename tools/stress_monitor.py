
import psutil
import time
import os
import json

def monitor_stress(duration_sec=60, interval_sec=5):
    print(f"--- Iniciando Monitor de Estres Industrial (Duracion: {duration_sec}s) ---")
    logs = []
    start_time = time.time()
    
    try:
        while time.time() - start_time < duration_sec:
            cpu = psutil.cpu_percent(interval=None)
            ram = psutil.virtual_memory().percent
            ram_mb = psutil.virtual_memory().used / (1024 * 1024)
            
            status = {
                "timestamp": time.strftime("%H:%M:%S"),
                "cpu_percent": cpu,
                "ram_percent": ram,
                "ram_used_mb": round(ram_mb, 2)
            }
            logs.append(status)
            print(f"[{status['timestamp']}] CPU: {cpu}% | RAM: {ram}% ({status['ram_used_mb']} MB)")
            time.sleep(interval_sec)
            
        # Save stress log
        log_path = "logs/stress_monitor.json"
        os.makedirs("logs", exist_ok=True)
        with open(log_path, "w", encoding="utf-8") as f:
            json.dump(logs, f, indent=4)
        print(f"--- Log de estres guardado en {log_path} ---")
        
    except Exception as e:
        print(f"Error en monitor: {e}")

if __name__ == "__main__":
    monitor_stress()
