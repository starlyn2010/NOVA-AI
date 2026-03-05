import sys
import os
import yaml
import re

# Core components that are absolutely needed for initial type checking or routing
from core.router.semantic_router import SemanticRouter
from core.router.supervisor import Supervisor
from core.llm.integrator import NovaIntegrator
from core.skills.loader import SkillLoader

from core.security.env_loader import load_nova_env

class Orchestrator:
    def __init__(self):
        load_nova_env()
        print("Inicializando Nova Orchestrator (Arquitectura Unificada v2.7.1 - Intelligence Plus)...")
        self.test_mode = os.getenv("NOVA_TEST_MODE", "").strip().lower() in {"1", "true", "mock"}
        self.router = SemanticRouter()
        self.supervisor = Supervisor()
        self.integrator = NovaIntegrator()
        
        # Load hybrid models from config
        config_path = os.path.join(os.path.dirname(__file__), "config.yaml")
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                config = yaml.safe_load(f)
            self.coding_model = config["llm"].get("coding_model", "deepseek-coder:1.3b")
            self.chat_model = config["llm"].get("chat_model", "deepseek-coder:1.3b")
        except:
            self.coding_model = "deepseek-coder:1.3b"
            self.chat_model = "deepseek-coder:1.3b"

        self.last_intent = None
        
        # Core Components
        from core.memory.engine import MemoryEngine
        from core.memory.profile import ProfileManager
        
        self.memory = MemoryEngine()
        self.profile = ProfileManager()
        self.skills = SkillLoader()
        
        # Lazy Engines Module Map (Dynamic Import)
        # Lazy Engines Module Map (Dynamic Import)
        self._engine_map = {
            # ── Core Engines ────────────────────────────────────────
            "programming": ("engines.programming.code_engine", "CodeEngine"),
            "mathematics": ("engines.mathematics.math_engine", "MathEngine"),
            "creative": ("engines.creative.creative_engine", "CreativeEngine"),
            "knowledge": ("engines.knowledge.knowledge_engine", "KnowledgeEngine"),
            "tools": ("engines.tools.tools_engine", "ToolsEngine"),
            "search": ("engines.search.web_engine", "WebSearchEngine"),
            "files": ("engines.files.file_engine", "FileEngine"),
            "vision": ("engines.vision.vision_engine", "VisionEngine"),
            "visuals": ("engines.visuals.visual_engine", "VisualEngine"),
            "audio": ("engines.audio.audio_engine", "AudioEngine"),
            "crawl": ("engines.search.web_crawler_engine", "SmartBrowserEngine"),
            "watchdog": ("engines.tools.watchdog_engine", "WatchdogSystem"),
            "comm": ("engines.tools.comm_engine", "CommunicationEngine"),
            "shield": ("core.security.shield", "SecurityShield"),
            "maintenance": ("core.memory.compaction", "CompactionEngine"),
            "wiki": ("core.knowledge.wiki_generator", "WikiGenerator"),
            "ui": ("ui.controller", "UIController"),
            # ── Connectors v2.8.0 ──────────────────────────────────
            "telegram": ("connectors.telegram_connector", "TelegramConnector"),
            "whatsapp": ("connectors.whatsapp_connector", "WhatsAppConnector"),
            "vscode": ("connectors.vscode_connector", "VSCodeConnector"),
            "pixazo": ("connectors.pixazo_connector", "PixazoConnector"),
            "canva": ("connectors.canva_connector", "CanvaConnector"),
            "youtube": ("connectors.youtube_connector", "YouTubeConnector"),
            "github": ("connectors.github_connector", "GitHubConnector"),
            "google": ("connectors.google_connector", "GoogleConnector"),
            "notion": ("connectors.notion_connector", "NotionConnector"),
            "spotify": ("connectors.spotify_connector", "SpotifyConnector"),
            "wolfram": ("connectors.services_connector", "WolframConnector"),
            "trello": ("connectors.services_connector", "TrelloConnector"),
            "vercel": ("connectors.services_connector", "VercelConnector"),
        }
        self.engines = {} 

    def process_request(self, user_input: str, max_turns: int = 3, is_voice: bool = False):
        """
        Versión final Phase 16 con Bucle de Pensamiento Avanzado y Self-Healing.
        """
        if self.test_mode:
            max_turns = 1

        current_input = user_input
        last_response = None
        observations = []

        for turn in range(max_turns):
            if not self.test_mode:
                print(f"\n--- Turno de Pensamiento {turn+1}/{max_turns} ---")
            
            # 1. Intent Resolution (Inteligencia de Nivel 5)
            final_intent = None
            # El Supervisor decide si seguimos con el intent anterior o cambiamos
            if self.last_intent and self.last_intent != "social":
                decision = self.supervisor.decide(self.last_intent, current_input)
                if decision == "CONTINUE":
                    if not self.test_mode:
                        print(f"[Supervisor] Continuando con la intención: {self.last_intent}")
                    final_intent = self.last_intent
            
            if final_intent is None:
                route_result = self.router.route(current_input)
                final_intent = route_result["intent"]

                # Nivel 5: Verificación por LLM si el router matemático es inseguro
                if route_result.get("confidence", 0) < 0.5 and not self.test_mode:
                    print(f"[Level 5] Router inseguro ({route_result.get('confidence', 0):.2f}). Verificando con LLM...")
                    final_intent = self._llm_intent_verification(current_input)

            # Intent override for visuals (Regla fuerte)
            if any(kw in current_input.lower() for kw in ["gráfico", "grafica", "visualiza"]):
                final_intent = "visuals"
            
            # 2. Add Observations and Semantic Context
            context_prefix = ""
            if observations:
                context_prefix = "OBSERVACIONES DE EJECUCIÓN (SELF-HEALING):\n" + "\n".join(observations) + "\n\n"
            
            # 3. Context (Memory & Skills)
            # El MemoryEngine ahora busca semánticamente por defecto
            memory_context = ""
            if (not self.test_mode) and final_intent != "social":
                memory_context = self.memory.get_context_string(current_input)
            
            # 4. Engine Process (Single Execution - Ultra Lazy Mode)
            engine_output = {}
            active_engine = self.engines.get(final_intent)
            
            # Dynamic Import & Instantiation
            if not active_engine and final_intent in self._engine_map:
                try:
                    module_path, class_name = self._engine_map[final_intent]
                    import importlib
                    module = importlib.import_module(module_path)
                    engine_cls = getattr(module, class_name)
                    active_engine = engine_cls()
                    self.engines[final_intent] = active_engine
                except Exception as e:
                    print(f"[Orchestrator] Error dynamicaly loading engine {final_intent}: {e}")

            if active_engine:
                try:
                    engine_output = active_engine.process(current_input)
                    if not isinstance(engine_output, dict):
                         engine_output = {"status": "error", "message": "Motor devolvió un tipo no válido"}
                except Exception as e:
                    engine_output = {"status": "error", "message": f"Error fatal en motor {final_intent}: {str(e)}"}
            else:
                engine_output = {"status": "warning", "message": f"Motor para '{final_intent}' no disponible."}
            
            # Additional integration (if needed and NOT already called)
            if final_intent == "programming" and active_engine != self.engines.get("tools"):
                 # Solo si programming no es el mismo que tools (en v2.7 son distintos pero CodeEngine llama a Tools)
                 pass # CodeEngine ya maneja esto internamente

            # 5. Smart Skill Injection (Anti-Bloat Level 5)
            if (not self.test_mode) and final_intent != "social":
                # Seleccionar skills relevantes según la intención para evitar 'prompt bloat'
                all_skills = self.skills.list_skills()
                relevant_skills = []
                
                if final_intent in ["programming", "tools", "files"]:
                    relevant_skills = [s for s in all_skills if any(kw in s for kw in ["code", "git", "api", "test", "json", "doc", "sql", "regex", "refactor"])]
                elif final_intent in ["creative", "knowledge"]:
                    relevant_skills = [s for s in all_skills if any(kw in s for kw in ["write", "story", "joke", "poem", "summarize", "tutor"])]
                
                # Fallback: Solo las primeras 5 si no hay match claro, para no saturar 2048 tokens
                if not relevant_skills:
                    relevant_skills = all_skills[:5]

                skill_info = "\n".join([self.skills.get_skill_instructions(s) for s in relevant_skills])
                if skill_info:
                    engine_output["skills_context"] = skill_info

            # 5. Model Selection
            target_model = self.coding_model if final_intent in ["programming", "files"] else self.chat_model
            
            # 6. Integrate & Think
            self.integrator.set_memory_summary(memory_context)
            self.integrator.set_user_context("Usuario", "Preferencias estándar de producto")
            
            result_pkg = self.integrator.process(
                context_prefix + current_input, 
                engine_output, 
                final_intent, 
                model_override=target_model
            )
            
            last_response = {
                "text": result_pkg["text"],
                "raw": engine_output,
                "action_request": engine_output.get("action_request")
            }

            # --- Lógica de Self-Healing ---
            # Si hay una acción solicitada, en el futuro Nova esperará el resultado.
            # Por ahora, capturamos si hubo un error previo para inyectarlo en 'observations'
            if last_response.get("raw", {}).get("error"):
                observations.append(f"Error en motor: {last_response['raw']['error']}")
            
            # Si no hay acción pendiente, salimos del bucle
            if not last_response.get("action_request"):
                break
            
            # En v2.7.0 cortamos aquí para que el usuario apruebe la acción en la UI
            # pero el sistema ya sabe recolectar 'observations' si re-entramos
            break 

        # Almacenar en memoria
        if (not self.test_mode) and (final_intent != "social" or len(user_input) > 20):
            self.memory.store(
                content=f"User: {user_input} | Nova: {last_response['text'][:100]}...",
                source="interaction",
                metadata={"intent": final_intent}
            )
        
        self.last_intent = final_intent if final_intent != "social" else self.last_intent

        # --- Voice Response Trigger ---
        if is_voice and last_response and last_response.get("text"):
            try:
                # Lazy load audio engine if not present
                if "audio" not in self.engines:
                    mod_path, cls_name = self._engine_map["audio"]
                    mod = __import__(mod_path, fromlist=[cls_name])
                    self.engines["audio"] = getattr(mod, cls_name)()
                
                # Speak only the main text, removing artifacts for voice
                clean_text = re.sub(r'<artifact.*?>.*?</artifact>', '', last_response["text"], flags=re.DOTALL).strip()
                if clean_text:
                    self.engines["audio"].say(clean_text)
            except Exception as e:
                print(f"[Orchestrator] Error en trigger de voz: {e}")

        return last_response

    def _llm_intent_verification(self, user_input: str) -> str:
        """
        Fallback de Nivel 5: Pregunta al LLM la intención cuando hay ambigüedad.
        """
        try:
            prompt = (
                f"Analiza la intención del usuario. Responde ÚNICAMENTE con la palabra técnica correspondiente de esta lista:\n"
                f"programming, mathematics, creative, search, files, vision, visuals, knowledge, social.\n\n"
                f"Mensaje del usuario: '{user_input}'\n"
                f"Intención (una sola palabra):"
            )
            # Procesamiento ultra-rápido
            res = self.integrator.process(prompt, {}, "intent_verification", model_override=self.chat_model)
            intent = res["text"].lower().strip().split('\n')[0].replace(".", "").replace(":", "")
            
            valid_intents = list(self._engine_map.keys()) + ["social"]
            if intent in valid_intents:
                print(f"[Level 5] LLM resolvió: {intent}")
                return intent
        except Exception as e:
            print(f"[Level 5] Error en verificación LLM: {e}")
            
        return "social"

    def execute_script(self, script_relative_path: str):
        import subprocess
        # Hardening: Solo permitir ejecución desde carpetas de herramientas o entrenamiento
        base_dir = os.path.dirname(os.path.abspath(__file__))
        full_path = os.path.normpath(os.path.join(base_dir, script_relative_path))
        
        allowed_dirs = [
            os.path.join(base_dir, "tools"),
            os.path.join(base_dir, "training")
        ]
        
        is_allowed = False
        for d in allowed_dirs:
            # Usar commonpath para evitar bypass de prefijos (ej. tools_evil)
            try:
                if os.path.commonpath([d, full_path]) == d:
                    is_allowed = True
                    break
            except ValueError:
                continue
        
        if not is_allowed:
            return {"status": "error", "message": "Acceso denegado: Ejecución restringida a carpetas autorizadas."}

        if not os.path.exists(full_path):
            return {"error": f"Script no encontrado: {full_path}"}
        
        try:
            python_exe = sys.executable
            # Usar cwd para evitar fugas de contexto
            result = subprocess.run([python_exe, full_path], capture_output=True, text=True, check=True, cwd=base_dir)
            return {"status": "success", "output": result.stdout}
        except Exception as e:
            return {"status": "error", "message": f"Error de ejecución: {str(e)}"}

if __name__ == "__main__":
    nova = Orchestrator()
    print("Nova lista. Escribe 'salir' para terminar.")
    while True:
        try:
            user_in = input("\nUsuario: ")
            if user_in.lower() in ["salir", "exit"]: break
            response = nova.process_request(user_in)
            print(f"\nNova: {response}")
        except Exception as e:
            print(f"Error: {e}")
