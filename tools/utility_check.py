
import time
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from core.llm.integrator import NovaIntegrator

def manual_utility_check():
    integrator = NovaIntegrator()
    # Forzamos un timeout mas largo solo para esta prueba de calidad
    integrator.client.request_timeout = 160 
    
    prompt = "Si tengo 3 manzanas y me regalas 2, pero una se pudre, ¿cuantas manzanas comestibles tengo? Explica tu razonamiento brevemente."
    print(f"PROMPT: {prompt}")
    print("PENSANDO...")
    
    start = time.time()
    try:
        # Usamos audit_mode para evitar plantillas
        os.environ["NOVA_AUDIT_MODE"] = "true"
        resp = integrator.process(prompt, {}, "logic")
        elapsed = time.time() - start
        
        text = resp.get("text", "")
        print(f"\nTIEMPO: {elapsed:.2f}s")
        print(f"RESPUESTA:\n{text}")
        
        # Validacion de utilidad
        is_useful = "4" in text and "manzana" in text.lower()
        print(f"\n¿ES UTIL/CORRECTO?: {'SI' if is_useful else 'NO'}")
        
    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    manual_utility_check()
