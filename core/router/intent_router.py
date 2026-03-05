import yaml
import re
import os
from typing import Dict, List, Tuple

class IntentRouter:
    def __init__(self, config_path: str = "config.yaml"):
        self.base_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        self.signals = self._load_signals()
        
    def _load_signals(self) -> Dict:
        signals_path = os.path.join(self.base_path, "core", "router", "signals.yaml")
        try:
            with open(signals_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except Exception as e:
            print(f"Error loading signals: {e}")
            return {}

    def route(self, user_input: str) -> Dict:
        """
        Determines the intent of the user input based on predefined signals.
        Returns a dictionary with 'intent', 'confidence', 'method', and 'justification'.
        """
        scores = self._calculate_scores(user_input)
        
        # If we have a clear winner (> 0.4 for strictness, or adjusted per need)
        # config says min_confidence 0.6, let's respect logic but ensure we return something
        if scores:
             best_match = scores[0]
             intent, score = best_match
             
             # Heuristic: if score is decent, return it.
             # If score is very low, we might fallback to LLM (implemented in Orchestrator later)
             # For now, return the best rule-based match
             
             return {
                 "intent": intent,
                 "confidence": score,
                 "method": "rules",
                 "justification": f"Detected by top signal match: {intent} ({score:.2f})"
             }
        
        return {
            "intent": "social", # Default fallback
            "confidence": 0.0,
            "method": "default",
            "justification": "No signals detected"
        }

    def _calculate_scores(self, text: str) -> List[Tuple[str, float]]:
        scores = {}
        text_lower = text.lower()
        
        for intent, config in self.signals.items():
            score = 0
            
            # Keywords matching
            for kw in config.get("keywords", []):
                if kw in text_lower:
                    score += 0.15
                    
            # Pattern matching
            for pattern in config.get("patterns", []):
                try:
                    if re.search(pattern, text, re.IGNORECASE):
                        score += 0.25
                except re.error:
                    pass
            
            # Weighted normalization (simple saturation at 1.0)
            final_score = min(score, 1.0)
            
            # Add base weight bias
            # final_score += config.get("weight", 0) 
            # Actually, priority handling handles ties, but let's stick to calculated score
            
            if final_score > 0:
                scores[intent] = final_score

        # Sort by score descending, then by priority (lower priority number is better)
        # We need priority from config
        sorted_scores = sorted(
            scores.items(),
            key=lambda item: (
                item[1], 
                -self.signals[item[0]].get("priority", 99)
            ), 
            reverse=True
        )
        
        return sorted_scores
