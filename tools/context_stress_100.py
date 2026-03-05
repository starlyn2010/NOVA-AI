
import time
import json
import os
import sys

# Add root
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from core.llm.integrator import NovaIntegrator

def run_context_stress_100():
    integrator = NovaIntegrator()
    # Explicitly ensure we are NOT in test_mode or audit_mode logic fallbacks
    # unless intended. We want real LLM responses.
    os.environ["NOVA_AUDIT_MODE"] = "true"
    
    # Configuramos un gran proyecto: Construccion de un Sistema Solar narrativo/logico
    log_file = "logs/context_stress_100.log"
    os.makedirs("logs", exist_ok=True)
    
    print(f"--- Iniciando STRESS DE CONTEXTO (100 Turnos): Nova-Ultra ---")
    
    results = []
    current_context_summary = "Sistema Solar Nova-1"
    
    for i in range(1, 101):
        if i <= 30:
            prompt = f"Turno {i}: Añade un planeta llamado 'Planeta-{i}' al sistema {current_context_summary}. Describe su clima en una frase corta."
        elif i <= 60:
            prompt = f"Turno {i}: En el 'Planeta-{i-20}', ¿recuerdas que clima dije que tenia? Si no lo sabes, inventa uno coherente pero confirma si lo recordaste."
        elif i <= 90:
            prompt = f"Turno {i}: Escribe una linea de codigo Python para simular la orbita de 'Planeta-{i-50}'."
        else:
            prompt = f"Turno {i}: Haz un resumen de los 3 planetas mas interesantes que hemos creado hasta ahora en este chat."

        print(f"[{i}/100] Enviando prompt...", end="\r")
        
        start = time.time()
        try:
            # Note: integrator.process handles dynamic_memory.add_turn internally
            resp = integrator.process(prompt, {}, "logic")
            elapsed = time.time() - start
            
            text = resp.get("text", "")
            meta = resp.get("meta", {})
            
            results.append({
                "turn": i,
                "elapsed": elapsed,
                "status": "OK",
                "length": len(text)
            })
            
            with open(log_file, "a", encoding="utf-8") as f:
                f.write(f"--- TURNO {i} ({elapsed:.2f}s) ---\nPROMPT: {prompt}\nRESP: {text}\n\n")
                
        except Exception as e:
            print(f"\n[ERROR] en turno {i}: {e}")
            break

    print(f"\n--- STRESS COMPLETADO ---")
    # Resumen final de latencia vs contexto
    avg_latency = sum(r["elapsed"] for r in results) / len(results)
    print(f"Latencia promedio: {avg_latency:.2f}s")

if __name__ == "__main__":
    run_context_stress_100()
