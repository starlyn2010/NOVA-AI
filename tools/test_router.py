import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.router.semantic_router import SemanticRouter

router = SemanticRouter()

tests = [
    "dibuja un gráfico de barras",
    "hazme una ilustración de los datos", # Sinónimo de visual
    "repara este error en el script",    # Sinónimo de programming/tools
    "cuéntame una fábula",                # Sinónimo de creative
    "investiga sobre los leones",         # Sinónimo de search
    "qué hay en esta carpeta"             # Sinónimo de files
]

print("--- Test de Enrutado Semántico ---")
for t in tests:
    res = router.route(t)
    print(f"Input: '{t}' -> Intent: {res['intent']} (Conf: {res['confidence']:.2f}, Metodo: {res['method']})")
