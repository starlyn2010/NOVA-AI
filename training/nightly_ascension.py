import subprocess
import time
import os

def run_nightly_ascension():
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    print("Starting NIGHTLY ASCENSION of Nova...")
    
    scripts = [
        "training/tool_distiller.py",
        "training/cerebro_train.py"
    ]
    
    # Bucle infinito para procesamiento profundo hasta la mañana
    while True:
        for script in scripts:
            script_path = os.path.join(root, script)
            print(f"Processing cognitive block: {script}")
            try:
                subprocess.run(["python", script_path], check=True)
            except Exception as e:
                print(f"⚠️ Error en bloque {script}: {e}")
            
        print("Cycle completed. Consolidating synapses (waiting for next block)...")
        time.sleep(300) # Pausa de 5 minutos entre ciclos para no quemar la CPU

if __name__ == "__main__":
    run_nightly_ascension()
