import logging
import os
import sys
import yaml
import json
from typing import Dict, Any, Optional

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.router.intent_router import IntentRouter
from core.router.supervisor import Supervisor
from core.llm.integrator import NovaIntegrator
from core.security.shield import SecurityShield
from core.memory.engine import MemoryEngine

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("NovaOrchestrator")

class Orchestrator:
    """
    Nova Central Orchestrator: Level 5 Intent Routing & Multi-Engine Integration.
    Acts as the brain that connects the UI, Router, Security, and LLM.
    """
    def __init__(self, config_path: str = "config.yaml"):
        self.base_path = os.path.dirname(os.path.abspath(__file__))
        self.config = self._load_config(config_path)
        
        # Initialize Core Components
        self.router = IntentRouter()
        self.supervisor = Supervisor()
        self.integrator = NovaIntegrator()
        self.security = SecurityShield()
        self.memory = MemoryEngine()
        
        # Internal State
        self.current_intent = "social"
        self.version = self.config.get("system", {}).get("version", "2.8.0")
        
        logger.info(f"Nova Orchestrator v{self.version} initialized.")

    def _load_config(self, path: str) -> Dict:
        try:
            with open(os.path.join(self.base_path, path), 'r', encoding='utf-8') as f:
                return yaml.safe_load(f) or {}
        except Exception as e:
            logger.error(f"Error loading config: {e}")
            return {}

    def process_request(self, user_input: str, is_voice: bool = False) -> Dict[str, Any]:
        """
        Main pipeline: Security -> Routing -> Logic Execution -> LLM Synthesis
        """
        logger.info(f"Processing request: {user_input[:50]}...")
        
        # 1. Security Pre-scan (if input looks like a path)
        candidate_path = (user_input or "").strip()
        if ("/" in candidate_path or "\\" in candidate_path) and "://" not in candidate_path:
            if os.path.exists(candidate_path) and os.path.isfile(candidate_path):
                security_check = self.security.scan_file(candidate_path)
                if security_check.get("risk_level") == "HIGH":
                    return {
                        "text": f"Acceso denegado. El archivo presenta un nivel de riesgo CRÍTICO ({security_check.get('risk_score')}).",
                        "engine": "security_shield",
                        "status": "blocked"
                    }

        # 2. Intent Routing
        decision = self.supervisor.decide(self.current_intent, user_input)
        
        if decision == "CHANGE" or self.current_intent == "social":
            route_info = self.router.route(user_input)
            self.current_intent = route_info.get("intent", "social")
            logger.info(f"New intent detected: {self.current_intent}")
        else:
            logger.info(f"Staying with current intent: {self.current_intent}")

        # 3. Context Injection (RAG)
        context = self.memory.get_context_string(user_input)
        
        # 4. Engine Interaction (Simplified for MVP, usually mapped to specific classes)
        # Note: In a full implementation, each intent maps to a specialized engine.py
        engine_outputs = {"status": "success", "context": context}
        
        # 5. LLM Synthesis
        response = self.integrator.process(
            original_request=user_input,
            engine_outputs=engine_outputs,
            engine_name=self.current_intent
        )

        # 6. Memory Reinforcement
        if response.get("text"):
            self.memory.store(
                content=f"User: {user_input} | Nova: {response['text']}",
                source="conversation",
                metadata={"intent": self.current_intent}
            )

        return {
            "text": response.get("text", "Error en procesamiento."),
            "engine": self.current_intent,
            "status": "success",
            "metadata": response.get("meta", {})
        }

    def execute_script(self, script_path: str) -> Dict[str, Any]:
        """Secure script execution placeholder."""
        # This would integrate with the SecurityShield allowlist in the next step
        return {"error": "Execution requires SecurityShield allowlist verification."}

if __name__ == "__main__":
    # Smoke test
    orch = Orchestrator()
    print(orch.process_request("Hola Nova, ¿quién eres?"))
