import os
import sys
import time

sys.path.append(os.getcwd())

def verify_performance():
    print("--- INICIANDO VERIFICACIÓN DE RENDIMIENTO (ARRANQUE < 2s) ---")
    
    try:
        start_time = time.time()
        from orchestrator import Orchestrator
        nova = Orchestrator()
        end_time = time.time()
        
        startup_time = end_time - start_time
        print(f"Tiempo de Arranque detectado: {startup_time:.4f} s")
        
        if startup_time < 2.0:
            print(f"PASS: Arranque ultra-rápido ({startup_time:.2f}s < 2s)")
            sys.exit(0)
        else:
            print(f"FAILED: El arranque excedió los 2 segundos ({startup_time:.2f}s)")
            sys.exit(1)
            
    except Exception as e:
        print(f"ERROR en la prueba: {e}")
        sys.exit(1)

if __name__ == "__main__":
    verify_performance()
