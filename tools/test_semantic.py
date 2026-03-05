import sys
import os
# Añadir el directorio raíz al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.memory.semantic_rag import SemanticMemory

# Test simple semantic matching
mem = SemanticMemory("data/memory.json")
mem.add_document("Fuimos de vacaciones a la playa y estaba muy soleado.")
mem.add_document("La programación en Python es divertida y poderosa.")

print("Test 1: Palabra exacta 'Python'")
print(mem.find_relevant("Python"))

print("\nTest 2: Concepto 'vacaciones' (debería traer la playa)")
print(mem.find_relevant("vacaciones"))

print("\nTest 3: Concepto 'mar' (debería traer la playa semánticamente)")
print(mem.find_relevant("mar"))
