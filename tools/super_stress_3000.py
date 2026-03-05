
import time
import json
import os
import sys

# Add root
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from core.llm.integrator import NovaIntegrator

def generate_3000_prompts():
    prompts = []
    # 500 Faciles: Logica
    for i in range(500):
        prompts.append({"id": f"logic_easy_{i}", "category": "logic", "prompt": f"Calcula {i} + {i+1} y dime el resultado directamente."})
    
    # 500 Faciles: Saludos
    greetings = ["Hola", "Buenos dias", "Que tal", "Como estas", "Hablame de ti"]
    for i in range(500):
        prompts.append({"id": f"social_easy_{i}", "category": "social", "prompt": f"{greetings[i % len(greetings)]} Nova ({i})"})
    
    # 1000 Fuertes: Codigo
    for i in range(1000):
        prompts.append({"id": f"code_hard_{i}", "category": "code", "prompt": f"Escribe un script en Python que realice una operacion matematica compleja numero {i} usando solo tipos nativos."})
    
    # 1000 Fuertes: Razonamiento
    for i in range(1000):
        prompts.append({"id": f"reasoning_hard_{i}", "category": "logic", "prompt": f"Si un tren sale de A a las {i % 24}:00 y llega a B en {i % 10 + 1} horas, ¿a que hora llega? Explica paso a paso."})
    
    return prompts

def run_3000_audit():
    integrator = NovaIntegrator()
    prompts = generate_3000_prompts()
    results = []
    
    log_file = "logs/super_audit_ultra.log"
    os.makedirs("logs", exist_ok=True)
    
    print(f"--- Iniciando GRAN AUDITORIA 3000: Nova-Ultra ---")
    
    start_all = time.time()
    for i, test in enumerate(prompts):
        # En una operacion de 3000, solo imprimimos cada 10 para no saturar la consola
        if i % 10 == 0:
            print(f"Procesando {i}/3000...", end="\r")
            
        start = time.time()
        try:
            resp = integrator.process(test["prompt"], {}, test["category"])
            elapsed = time.time() - start
            
            text = resp.get("text", "")
            meta = resp.get("meta", {})
            
            status = "REAL"
            if meta.get("fallback_triggered"):
                status = "TEMPLATED"
            
            results.append({
                "id": test["id"],
                "status": status,
                "time": elapsed,
                "quality": "WARN" if "low_quality_detected" in str(meta) else "OK"
            })
            
            with open(log_file, "a", encoding="utf-8") as f:
                ts = time.strftime("%Y-%m-%d %H:%M:%S")
                f.write(f"{ts} - {test['id']} - {status} - {elapsed:.2f}s\n")
                
        except Exception as e:
            results.append({"id": test["id"], "status": "ERROR", "error": str(e)})
            with open(log_file, "a", encoding="utf-8") as f:
                ts = time.strftime("%Y-%m-%d %H:%M:%S")
                f.write(f"{ts} - {test['id']} - ERROR - {str(e)}\n")

    total_time = time.time() - start_all
    summary = {
        "total_tests": len(prompts),
        "total_time_sec": total_time,
        "avg_time_ms": (total_time / 3000) * 1000,
        "results": results
    }
    
    with open("logs/super_audit_ultra_summary.json", "w") as f:
        json.dump(summary, f, indent=4)
    
    print(f"\n--- AUDITORIA COMPLETADA en {total_time/60:.2f} minutos ---")

if __name__ == "__main__":
    run_3000_audit()
