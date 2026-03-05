import os
import sys

def get_dir_size(start_path = '.'):
    total_size = 0
    if not os.path.exists(start_path):
        return 0
    for dirpath, dirnames, filenames in os.walk(start_path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            if not os.path.islink(fp):
                total_size += os.path.getsize(fp)
    return total_size

def verify_no_download():
    print("--- INICIANDO VERIFICACIÓN DE NO-DESCARGA (LAZY LOAD CHECK) ---")
    
    whisper_cache = os.path.join(os.environ.get('USERPROFILE', ''), '.cache', 'whisper')
    playwright_cache = os.path.join(os.environ.get('LOCALAPPDATA', ''), 'ms-playwright')
    
    size_whisper_before = get_dir_size(whisper_cache)
    size_web_before = get_dir_size(playwright_cache)
    
    print(f"Caché Whisper inicial: {size_whisper_before / (1024*1024):.2f} MB")
    print(f"Caché Playwright inicial: {size_web_before / (1024*1024):.2f} MB")
    
    try:
        sys.path.append(os.getcwd())
        from orchestrator import Orchestrator
        nova = Orchestrator() # Inicialización base
        
        size_whisper_after = get_dir_size(whisper_cache)
        size_web_after = get_dir_size(playwright_cache)
        
        print(f"Caché Whisper final: {size_whisper_after / (1024*1024):.2f} MB")
        print(f"Caché Playwright final: {size_web_after / (1024*1024):.2f} MB")
        
        if size_whisper_after > size_whisper_before or size_web_after > size_web_before:
            print("FAILED: Se detectó descarga de modelos/binarios durante el arranque.")
            sys.exit(1)
        else:
            print("PASS: No hubo descargas automáticas (Lazy Load funcionando).")
            sys.exit(0)
            
    except Exception as e:
        print(f"ERROR: Fallo en prueba de descargas: {e}")
        sys.exit(1)

if __name__ == "__main__":
    verify_no_download()
