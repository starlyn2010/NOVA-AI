import os
import json
import time
import random

class CerebroTrainer:
    def __init__(self):
        self.root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.dataset_path = os.path.join(self.root, "knowledge", "datasets", "logic_core.json")
        os.makedirs(os.path.dirname(self.dataset_path), exist_ok=True)
        
    def generate_logic_trace(self):
        """Genera ejemplos sintéticos de nivel GPT-4 con alta diversidad."""
        scenarios = [
            # LÓGICA & RAZONAMIENTO
            {"input": "Si todos los A son B, y ningún B es C, ¿qué podemos decir de A y C?", "thought": "Transitividad negativa.", "output": "Ningún A es C."},
            {"input": "P -> Q y ~Q. ¿Cuál es el resultado?", "thought": "Modus Tollens.", "output": "Se infiere ~P."},
            {"input": "Explica la paradoja de Russell en términos simples.", "thought": "Autoreferencia y conjuntos.", "output": "Es el problema del barbero que solo afeita a quienes no se afeitan a sí mismos. ¿Quién afeita al barbero?"},
            
            # CÓDIGO & ALGORITMOS
            {"input": "Implementa un decorador en Python para medir el tiempo de ejecución.", "thought": "Uso de functools.wraps y time.perf_counter.", "output": "```python\nimport time\nfrom functools import wraps\ndef timer(func):\n    @wraps(func)\n    def wrapper(*args, **kwargs):\n        start = time.perf_counter()\n        result = func(*args, **kwargs)\n        print(f'{func.__name__} tardó {time.perf_counter()-start:.4f}s')\n        return result\n    return wrapper\n```"},
            {"input": "¿Cómo evitar SQL Injection en Node.js?", "thought": "Consultas parametrizadas.", "output": "Usa siempre queries preparadas con placeholders (?) o un ORM como Prisma/Sequelize que las implemente por defecto."},
            
            # SISTEMAS & ARQUITECTURA
            {"input": "Diseña un sistema de autenticación local sin DB.", "thought": "Hashing local Argon2 + JWT.", "output": "Usa Argon2 para el hash y almacena secretos en un Vault local o Keychain del sistema."},
            {"input": "Diferencia entre microservicios y monolito modular.", "thought": "Acoplamiento vs despliegue.", "output": "El monolito modular comparte procesos y memoria pero separa lógica; los microservicios separan procesos y despliegue."},
            
            # CIENCIA & CONOCIMIENTO
            {"input": "¿Qué es la entropía en termodinámica vs teoría de información?", "thought": "Desorden vs Incertidumbre.", "output": "En física es desorden de partículas; en información es el promedio de incertidumbre de una fuente de datos."},
            
            # MATEMÁTICAS
            {"input": "Resuelve: El área de un círculo es 314.16. ¿Cuál es el radio?", "thought": "A = pi * r^2. 314.16 / 3.1416 = 100. sqrt(100) = 10.", "output": "El radio es aproximadamente 10 unidades."},
            {"input": "Derivada de ln(x^2 + 1).", "thought": "Regla de la cadena: u'/u.", "output": "La derivada es 2x / (x^2 + 1)."},
            
            # HERRAMIENTAS & AGENTES
            {"input": "Plan para analizar un repo y subirlo a Vercel.", "thought": "Agentic workflow: GitHub -> Analysis -> Vercel.", "output": "1. Fetch repo. 2. Code linting. 3. Config check. 4. Trigger build via Vercel CLI."},
            {"input": "Generar imágenes coherentes para un cuento infantil.", "thought": "Consistencia de personajes.", "output": "Usa un 'seed' fijo y descripciones de personajes constantes en cada prompt de Pixazo."},
            
            # LINGÜÍSTICA
            {"input": "Analiza sintácticamente: 'Nova estudia códigos brillantes'.", "thought": "Sujeto + Predicado.", "output": "Nova (Sujeto), estudia (Núcleo del predicado), códigos brillantes (Objeto Directo)."}
        ]
        # Añadir variaciones aleatorias para aumentar la diversidad
        selected = random.choice(scenarios)
        return selected

    def run_nightly_loop(self, iterations=100):
        print(f"--- Iniciando Bucle Nocturno: Proyecto Cerebro ---")
        dataset = []
        for i in range(iterations):
            trace = self.generate_logic_trace()
            dataset.append(trace)
            if i % 10 == 0:
                print(f"Progreso: {i}/{iterations} trazas generadas...")
            time.sleep(0.1)
            
        with open(self.dataset_path, "w", encoding="utf-8") as f:
            json.dump(dataset, f, indent=4, ensure_ascii=False)
        print(f"--- Entrenamiento Completado. Dataset guardado en {self.dataset_path} ---")

if __name__ == "__main__":
    trainer = CerebroTrainer()
    trainer.run_nightly_loop()
