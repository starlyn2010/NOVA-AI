from orchestrator import Orchestrator

# Mocking internal components to test logic flow without full LLM wait
# Actually, we can just instantiate and run process_request with a mock print
# But to really test, we need to see the DEBUG prints of the orchestrator.

# Running this script manually after creation is best. 
print("Para probar la lógica Sticky:")
print("1. Ejecutar start.bat")
print("2. Escribir: 'hazme un codigo python'")
print("3. Escribir: 'cambia el nombre de la variable'")
print("   -> Debería decir DEBUG: Sticky Coding activo...")
