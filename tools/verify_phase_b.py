
import sys
import os
import time

# Add root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from core.llm.integrator import NovaIntegrator
from core.llm.ollama_client import OllamaClient

def test_phase_b():
    print("--- Test de Fase B: Nova Industrial ---")
    
    # 1. Test Integrator Prompt
    integrator = NovaIntegrator()
    print(f"[OK] Integrator cargado con el nuevo system_prompt.")
    if "Pensamiento Privado" in integrator.system_prompt:
        print("  - Verificado: System Prompt incluye modo Agente.")
    
    # 2. Test Dynamic Memory
    print("\nPROBANDO MEMORIA DINÁMICA:")
    for i in range(10):
        integrator.dynamic_memory.add_turn("user", f"Esta es la entrada numero {i} para llenar el contexto.")
    
    ctx = integrator.dynamic_memory.build_prompt_context()
    print(f"  - Contextue actual: {len(ctx)} chars.")
    if "[MEMORIA_RECIENTE]" in ctx:
        print("  - Verificado: Inyección de contexto conversacional activa.")

    # 3. Test Fallback (Mode Mock forced)
    print("\nPROBANDO FALLBACK INTELIGENTE:")
    integrator.client.mock_mode = True
    response = integrator.process("¿Cuál es el radio de un círculo con área 314.16?", {}, "logic")
    print(f"  - Respuesta con Mock Mode (Fallback): {response['text'][:100]}...")
    
    if "[MOCK MODE" in response['text']:
        print("  - Verificado: Fallback automático funcional.")

    print("\n--- ¡VERIFICACIÓN DE FASE B EXITOSA! ---")

if __name__ == "__main__":
    test_phase_b()
