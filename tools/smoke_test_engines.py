import sys
import os
import importlib
sys.path.append(os.getcwd())
from orchestrator import Orchestrator

def smoke_test():
    print("--- INICIANDO SMOKE TEST DE MOTORES (CONTRACT VALIDATION v2.7.1 - DYNAMIC) ---")
    nova = Orchestrator()
    results = {}
    
    # Probamos TODOS los motores definidos en el mapa dinámico
    engines_to_test = nova._engine_map
    
    for intent, (module_path, class_name) in engines_to_test.items():
        print(f"Testing {intent}...", end=" ")
        try:
            # Forzamos carga dinámica e instanciación
            module = importlib.import_module(module_path)
            engine_cls = getattr(module, class_name)
            engine_inst = engine_cls()
            
            # Nivel 5: Llamada formal de Auditoría (Audit-Proof)
            res = engine_inst.process("", health_check=True)
            
            # Nivel 5: Validación profunda del valor de 'status'
            valid_stats = ["success", "warning", "no_suggestions", "finished", "ready", "local_documents", "general_knowledge_llm"]
            status_val = res.get("status", "")
            
            if isinstance(res, dict) and status_val in valid_stats:
                print(f"PASS (status: {status_val})")
                results[intent] = "PASS"
            elif isinstance(res, dict) and "status" in res:
                # Caso especial: 'failed' o 'error' son contratos válidos pero indican fallo funcional
                print(f"WARNING (Contract OK but Functional {status_val.upper()})")
                results[intent] = f"WARNING ({status_val})"
            elif isinstance(res, dict):
                print("FAIL (missing 'status' key)")
                results[intent] = "FAIL (Missing 'status')"
            else:
                print(f"FAIL (returned {type(res)})")
                results[intent] = f"FAIL (Type: {type(res)})"
        except Exception as e:
            print(f"FAIL (Exception: {str(e)})")
            results[intent] = f"FAIL (Error: {str(e)})"
            
    print("\n--- RESUMEN FINAL ---")
    all_clean = True
    for intent, status in results.items():
        print(f"{intent.upper()}: {status}")
        if "FAIL" in status or "WARNING" in status:
            all_clean = False
            
    if all_clean:
        print("\nGO: Todos los motores cumplen el contrato y funcionalidad v2.7.1.")
        sys.exit(0)
    else:
        print("\nNO-GO: Se detectaron fallos o advertencias funcionales.")
        sys.exit(1)

if __name__ == "__main__":
    smoke_test()
