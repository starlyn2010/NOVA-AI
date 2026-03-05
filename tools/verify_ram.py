import os
import sys
import psutil
import time

sys.path.append(os.getcwd())

def get_ram_usage():
    process = psutil.Process(os.getpid())
    return process.memory_info().rss / (1024 * 1024) # MB

def verify_ram():
    print("--- INICIANDO VERIFICACIÓN DE RAM (UMBRAL 400MB) ---")
    
    ram_before = get_ram_usage()
    print(f"RAM Antes de Orchestrator: {ram_before:.2f} MB")
    
    try:
        from orchestrator import Orchestrator
        start_time = time.time()
        nova = Orchestrator()
        end_time = time.time()
        
        ram_after = get_ram_usage()
        increment = ram_after - ram_before
        startup_time = end_time - start_time
        
        print(f"RAM Después de Orchestrator: {ram_after:.2f} MB")
        print(f"Incremento: {increment:.2f} MB")
        print(f"Tiempo de Arranque: {startup_time:.2f} s")
        
        success = True
        if increment > 400:
            print("FAILED: Incremento de RAM > 400 MB")
            success = False
        
        if startup_time > 2.0:
            print("FAILED: Tiempo de arranque > 2 segundos")
            success = False
            
        if success:
            print("PASS: Consumo y rendimiento dentro de límites 8GB.")
            sys.exit(0)
        else:
            sys.exit(1)
            
    except Exception as e:
        print(f"ERROR: Fallo durante la inicialización: {e}")
        sys.exit(1)

if __name__ == "__main__":
    verify_ram()
