import os
import json

class SemanticMemory:
    """
    Memoria semántica ligera para Nova.
    Usa TF-IDF y Similitud de Coseno para encontrar conceptos relacionados.
    """
    def __init__(self, storage_path: str):
        self.storage_path = storage_path
        self.vectorizer = None  # Lazy setup
        self.documents = []
        self.vectors = None
        self._index_built = False
        self.load()

    def load(self):
        if os.path.exists(self.storage_path):
            try:
                with open(self.storage_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    # El MemoryEngine guarda un dict con "memories"
                    memories_dict = data.get("memories", {})
                    self.documents = [item.get("content", "") for item in memories_dict.values() if isinstance(item, dict)]
                # IMPORTANT: Do not build TF-IDF index during startup.
                # Build only on first semantic query/add to keep Nova boot fast.
                self.vectors = None
                self._index_built = False
            except Exception as e:
                print(f"Error cargando memoria semántica: {e}")

    def _ensure_index(self):
        if self._index_built:
            return
        if not self.documents:
            self.vectors = None
            self._index_built = True
            return

        from sklearn.feature_extraction.text import TfidfVectorizer
        if self.vectorizer is None:
            self.vectorizer = TfidfVectorizer(stop_words='english')
        self.vectors = self.vectorizer.fit_transform(self.documents)
        self._index_built = True

    def find_relevant(self, query: str, top_k: int = 3):
        if not self.documents:
            return []

        self._ensure_index()
        if self.vectors is None:
            return []

        from sklearn.metrics.pairwise import cosine_similarity
        import numpy as np

        query_vec = self.vectorizer.transform([query])
        similarities = cosine_similarity(query_vec, self.vectors).flatten()
        
        # Obtener los índices de los top_k más similares
        relevant_indices = similarities.argsort()[-top_k:][::-1]
        
        results = []
        for idx in relevant_indices:
            if similarities[idx] > 0.1: # Threshold mínimo de relevancia
                results.append(self.documents[idx])
        
        return results

    def add_document(self, content: str):
        """Añade un nuevo documento y regenera los vectores."""
        self.documents.append(content)
        # Rebuild lazily for performance; mark stale now.
        self._index_built = False
