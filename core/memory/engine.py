"""
Nova v2.7.0 - Memory Engine
Manages storage, search, reinforcement and pruning of MemoryUnits.
Ported from IA/src/memory/engine.py with JSON persistence added.
"""
from typing import List, Dict
from core.memory.unit import MemoryUnit
import json
import os
from core.memory.semantic_rag import SemanticMemory


class MemoryEngine:
    """
    Manages the collection of MemoryUnits.
    Handles storage, retrieval (search), lifecycle (pruning), and persistence.
    """
    def __init__(self, data_path: str = None):
        self.memories: Dict[str, MemoryUnit] = {}
        self.archive: Dict[str, MemoryUnit] = {}
        self._content_index: Dict[str, str] = {} # content_hash -> unit_id
        
        # Persistence path
        if data_path is None:
            data_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data")
        self.data_path = data_path
        self.memory_file = os.path.join(data_path, "memory.json")
        
        # Auto-load if file exists
        self.load()
        
        # Initialize semantic layer
        self.semantic = SemanticMemory(self.memory_file)

    def _get_content_hash(self, content: str) -> str:
        import hashlib
        return hashlib.md5(content.strip().encode('utf-8')).hexdigest()

    def store(self, content: str, source: str, metadata: Dict = None) -> MemoryUnit:
        """Creates and indexes a new memory."""
        unit = MemoryUnit(content=content, source=source, metadata=metadata or {})
        self.memories[unit.id] = unit
        
        # Index by content hash for O(1) retrieval from semantic hits
        self._content_index[self._get_content_hash(content)] = unit.id
        
        print(f"[Memory] Stored: {content[:40]}... (ID: {unit.id[:8]})")
        self.save()
        
        # Actualizar índice semántico
        self.semantic.add_document(content)
        return unit

    def search(self, query: str, min_confidence: float = 0.2, max_results: int = 3) -> List[MemoryUnit]:
        """
        Retrieves memories relevant to the query.
        Combines keyword search with semantic matching (RAG).
        """
        results = []
        query_words = set(query.lower().split())
        
        # 1. Keyword Search
        keyword_hits = []
        if query_words:
            for unit in self.memories.values():
                if unit.effective_confidence < min_confidence:
                    continue
                content_words = set(unit.content.lower().split())
                intersection = query_words.intersection(content_words)
                if intersection:
                    score = len(intersection) / len(query_words)
                    if score > 0.1:
                        keyword_hits.append((unit, score))
        
        # 2. Semantic Search (Light RAG)
        semantic_texts = self.semantic.find_relevant(query, top_k=max_results)
        semantic_hits = []
        for text in semantic_texts:
            c_hash = self._get_content_hash(text)
            unit_id = self._content_index.get(c_hash)
            if unit_id and unit_id in self.memories:
                semantic_hits.append((self.memories[unit_id], 0.8))
        
        # Fusionar y ordenar
        all_hits = keyword_hits + semantic_hits
        all_hits.sort(key=lambda x: x[1], reverse=True)
        
        seen_ids = set()
        unique_results = []
        for unit, score in all_hits:
            if unit.id not in seen_ids:
                unique_results.append(unit)
                seen_ids.add(unit.id)
        
        return unique_results[:max_results]

    def reinforce(self, unit_id: str):
        """Strengthens a memory after successful use."""
        if unit_id in self.memories:
            self.memories[unit_id].reinforce()
            self.save()

    def prune(self, threshold: float = 0.1):
        """Moves weak memories to archive."""
        to_archive = [uid for uid, unit in self.memories.items() 
                      if unit.effective_confidence < threshold]
        
        for uid in to_archive:
            unit = self.memories.pop(uid)
            self.archive[uid] = unit
            print(f"[Memory] Pruned: {unit.content[:30]}... (Conf: {unit.effective_confidence:.3f})")
        
        if to_archive:
            self.save()

    def get_context_string(self, query: str) -> str:
        """
        Returns a formatted string of relevant memories for injection into the LLM prompt.
        This is the main integration point with the Integrator.
        """
        relevant = self.search(query)
        if not relevant:
            return ""
        
        lines = ["MEMORIAS RELEVANTES:"]
        for unit in relevant:
            lines.append(f"- {unit.content} (fuente: {unit.source})")
            self.reinforce(unit.id)
        
        return "\n".join(lines)

    def get_stats(self) -> dict:
        return {
            "active_count": len(self.memories),
            "archive_count": len(self.archive)
        }

    # --- Persistence ---
    
    def save(self):
        """Save all memories to JSON file."""
        os.makedirs(self.data_path, exist_ok=True)
        data = {
            "memories": {uid: unit.to_dict() for uid, unit in self.memories.items()},
            "archive": {uid: unit.to_dict() for uid, unit in self.archive.items()}
        }
        try:
            with open(self.memory_file, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"[Memory] Save error: {e}")
    
    def load(self):
        """Load memories from JSON file if it exists."""
        if not os.path.exists(self.memory_file):
            return
        
        try:
            with open(self.memory_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            for uid, unit_data in data.get("memories", {}).items():
                unit = MemoryUnit.from_dict(unit_data)
                self.memories[uid] = unit
                self._content_index[self._get_content_hash(unit.content)] = uid
            
            for uid, unit_data in data.get("archive", {}).items():
                self.archive[uid] = MemoryUnit.from_dict(unit_data)
            
            stats = self.get_stats()
            print(f"[Memory] Loaded {stats['active_count']} active, {stats['archive_count']} archived memories.")
        except Exception as e:
            print(f"[Memory] Load error: {e}")
