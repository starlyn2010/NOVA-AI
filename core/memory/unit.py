"""
Nova v2.7.0 - Memory Unit
Atomic unit of memory with temporal decay and reinforcement.
Ported from IA/src/memory/unit.py and adapted for Nova.
"""
import time
import uuid
import math
from dataclasses import dataclass, field
from typing import Dict


@dataclass
class MemoryUnit:
    """
    Represents a single atomic unit of memory.
    Living data that decays over time and grows stronger with use.
    """
    content: str
    source: str
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    
    # Cognitive Properties
    base_confidence: float = 1.0
    creation_time: float = field(default_factory=time.time)
    last_accessed: float = field(default_factory=time.time)
    access_count: int = 1
    
    # Metadata
    metadata: Dict = field(default_factory=dict)
    
    # Decay: Lose 10% confidence per 24h of inactivity
    decay_rate: float = 0.1

    @property
    def effective_confidence(self) -> float:
        """
        Current confidence = (Base + Reinforcement) - DecayPenalty
        Clamped to [0.01, 1.5]
        """
        age_days = (time.time() - self.last_accessed) / 86400.0
        decay_penalty = self.decay_rate * age_days
        reinforcement_bonus = min(0.5, math.log(max(1, self.access_count)) * 0.1)
        current = (self.base_confidence + reinforcement_bonus) - decay_penalty
        return max(0.01, min(1.5, current))

    def reinforce(self):
        """Called when memory is successfully retrieved and used."""
        self.last_accessed = time.time()
        self.access_count += 1

    def to_dict(self) -> dict:
        """Serialize to dict for JSON persistence."""
        return {
            "id": self.id,
            "content": self.content,
            "source": self.source,
            "base_confidence": self.base_confidence,
            "creation_time": self.creation_time,
            "last_accessed": self.last_accessed,
            "access_count": self.access_count,
            "metadata": self.metadata,
            "decay_rate": self.decay_rate
        }

    @classmethod
    def from_dict(cls, data: dict) -> "MemoryUnit":
        """Deserialize from dict."""
        return cls(
            content=data["content"],
            source=data["source"],
            id=data.get("id", str(uuid.uuid4())),
            base_confidence=data.get("base_confidence", 1.0),
            creation_time=data.get("creation_time", time.time()),
            last_accessed=data.get("last_accessed", time.time()),
            access_count=data.get("access_count", 1),
            metadata=data.get("metadata", {}),
            decay_rate=data.get("decay_rate", 0.1)
        )
