from core.router.intent_router import IntentRouter
import time

router = IntentRouter()

inputs = [
    "hola",
    "hazme un codigo en py",
    "hazme un codigo en python",
    "hazme un cuento de un heroe y villano que sea corto"
]

print("--- TESTING ROUTER ---")
for text in inputs:
    start = time.time()
    result = router.route(text)
    elapsed = time.time() - start
    print(f"Input: '{text}'")
    print(f"Result: {result}")
    print(f"Time: {elapsed:.4f}s")
    print("-" * 20)
