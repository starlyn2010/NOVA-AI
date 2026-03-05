import yaml
import re
import os
from typing import Dict, List, Tuple

class SemanticRouter:
    """
    Enrutador de intenciones avanzado que utiliza semántica (TF-IDF) y reglas.
    Permite capturar sinónimos y conceptos sin necesidad de palabras exactas.
    """
    def __init__(self, signals_path: str = None):
        if signals_path is None:
            self.base_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            self.signals_path = os.path.join(self.base_path, "core", "router", "signals.yaml")
        else:
            self.signals_path = signals_path
        
        self.signals = self._load_signals()
        self.vectorizer = None
        self.intent_signatures = {}
        self.intents_list = []
        self.signatures_matrix = None
        # self._build_semantic_model() # Se llamará bajo demanda en route()

    def _load_signals(self) -> Dict:
        try:
            with open(self.signals_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except Exception as e:
            print(f"[Router] Error cargando señales: {e}")
            return {}

    def _build_semantic_model(self):
        """Construye las firmas semánticas de cada intención a partir de sus palabras clave."""
        from sklearn.feature_extraction.text import TfidfVectorizer
        if self.vectorizer is None:
            self.vectorizer = TfidfVectorizer(stop_words=None, ngram_range=(1, 2))
            
        documents = []
        self.intents_list = list(self.signals.keys())
        
        for intent in self.intents_list:
            config = self.signals[intent]
            # Combinar keywords en un "documento" que representa la intención
            kws = " ".join(config.get("keywords", []))
            documents.append(kws)
        
        if documents:
            self.signatures_matrix = self.vectorizer.fit_transform(documents)

    def route(self, user_input: str) -> Dict:
        """
        Determina la intención combinando Reglas (Regex) y Semántica (TF-IDF).
        """
        text_lower = user_input.lower()
        
        # 1. Fase de Reglas (Máxima Prioridad)
        # Si un patrón Regex coincide exactamente, ganamos por "fuerza bruta"
        for intent, config in self.signals.items():
            for pattern in config.get("patterns", []):
                try:
                    if re.search(pattern, user_input, re.IGNORECASE):
                        return {
                            "intent": intent,
                            "confidence": 1.0,
                            "method": "rules",
                            "justification": f"Coincidencia exacta por patrón: {pattern}"
                        }
                except re.error:
                    pass

        # 2. Fase Semántica (Sinónimos y Conceptos)
        if self.signatures_matrix is None:
            self._build_semantic_model()

        if self.signatures_matrix is not None:
            import numpy as np
            from sklearn.metrics.pairwise import cosine_similarity
            
            query_vec = self.vectorizer.transform([text_lower])
            similarities = cosine_similarity(query_vec, self.signatures_matrix).flatten()
            
            best_idx = np.argmax(similarities)
            best_score = similarities[best_idx]
            intent = self.intents_list[best_idx]
            
            # 3. Resolución de Conflictos y Pesos (Level 5)
            # Bonus por extensiones comunes para File/Vision
            if intent == "files" and any(ext in text_lower for ext in [".py", ".txt", ".js", ".json", ".yaml", ".md"]):
                best_score += 0.2
            if intent == "vision" and any(ext in text_lower for ext in [".png", ".jpg", ".jpeg", ".bmp"]):
                best_score += 0.2
            
            if best_score > 0.15: # Threshold de confianza semántica
                return {
                    "intent": intent,
                    "confidence": float(min(best_score, 1.0)),
                    "method": "semantic-plus",
                    "justification": f"Similitud semántica avanzada (N-Grams) con '{intent}' ({best_score:.2f})"
                }

        # 3. Fallback a Palabras Clave tradicionales
        for intent, config in self.signals.items():
            for kw in config.get("keywords", []):
                if kw in text_lower:
                    return {
                        "intent": intent,
                        "confidence": 0.5,
                        "method": "keywords",
                        "justification": f"Palabra clave detectada: {kw}"
                    }

        return {
            "intent": "social",
            "confidence": 0.0,
            "method": "default",
            "justification": "No se detectaron señales claras"
        }
