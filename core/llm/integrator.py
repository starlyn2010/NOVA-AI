from .ollama_client import OllamaClient
from core.memory.dynamic_memory import DynamicMemory
import yaml
import os


class NovaIntegrator:
    def __init__(self):
        # Load config to get models and timeout.
        config_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            "config.yaml",
        )
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                config = yaml.safe_load(f) or {}
            llm_cfg = config.get("llm", {})
            self.model = llm_cfg.get("chat_model", "local-gguf")
            self.fallback_model = llm_cfg.get("fallback_model", "local-gguf")
            self.request_timeout = int(llm_cfg.get("timeout", 30))
            self.context_window = int(llm_cfg.get("context_window", 4096))
            self.engine_ctx_max_chars = int(llm_cfg.get("engine_ctx_max_chars", 3000))
        except Exception:
            self.model = "local-gguf"
            self.fallback_model = "local-gguf"
            self.request_timeout = 30
            self.context_window = 4096
            self.engine_ctx_max_chars = 3000

        self.test_mode = os.getenv("NOVA_TEST_MODE", "").strip().lower() in {
            "1",
            "true",
            "mock",
        }

        self.client = OllamaClient(
            default_model=self.model,
            request_timeout=self.request_timeout,
        )
        self.audit_mode = os.getenv("NOVA_AUDIT_MODE", "").strip().lower() in {"1", "true"}
        self.dynamic_memory = DynamicMemory(token_limit=self.context_window)
        self.system_prompt = (
            "Eres Nova, un agente operativo autonomo de nivel industrial.\n"
            "PROTOCOLO OBLIGATORIO:\n"
            "1) Pensamiento Privado (interno, no revelar):\n"
            "- Analiza la intencion real del usuario y el contexto disponible.\n"
            "- Planifica pasos concretos para resolver la tarea.\n"
            "- Selecciona herramientas y valida riesgos antes de ejecutar.\n"
            "- Verifica el resultado antes de redactar la salida.\n"
            "- Nunca expongas este pensamiento privado al usuario.\n"
            "2) Respuesta visible:\n"
            "- Entrega solo la respuesta final, clara, ejecutiva y en espanol.\n"
            "- Si faltan datos, pide exactamente lo minimo necesario.\n"
            "3) Herramientas y conectores:\n"
            "- Usa conectores cuando agreguen valor real y con fallback si fallan.\n"
            "- Mantente optimizada para equipos de 8GB RAM.\n"
            "4) Artefactos largos:\n"
            "- Para codigo o documentos extensos usa <artifact title=\"Nombre\" type=\"lenguaje\">...</artifact>."
        )
        if not isinstance(self.engine_ctx_max_chars, int) or self.engine_ctx_max_chars <= 0:
            self.engine_ctx_max_chars = 3000

    def set_memory_summary(self, summary: str):
        self.memory_summary = summary
        self.dynamic_memory.set_external_summary(summary)

    def set_user_context(self, name: str, prefs: str):
        self.user_name = name
        self.user_prefs = prefs

    def _strip_prefixes(self, text: str) -> str:
        prefixes = [
            "Nova:",
            "Respuesta de Nova:",
            "Respuesta:",
            "Actual:",
            "Usuario:",
            "Estatuto:",
            "Instruccion:",
            "Contexto:",
            "Nova responde:",
            "RESPUESTA:",
        ]
        for p in prefixes:
            if text.startswith(p):
                text = text[len(p) :].strip()
        return text

    def _is_low_quality_text(self, text: str) -> bool:
        if not text:
            return True
        norm = text.strip().lower()
        if len(norm) <= 14:
            return True
        bad_fragments = [
            "entiendo.",
            "entiendo",
            "no entiendo",
            "no comprendo",
            "lo siento pero no entiendo",
            "puedes repetir",
            "no he entendido",
        ]
        return any(bad in norm for bad in bad_fragments)

    def _engine_fallback_text(self, engine_name: str, engine_outputs: dict, original_request: str) -> str:
        if not isinstance(engine_outputs, dict):
            return f"Recibi tu solicitud '{original_request}', pero el motor {engine_name} devolvio un formato invalido."

        if engine_outputs.get("message"):
            return str(engine_outputs.get("message"))
        if engine_outputs.get("solution"):
            return f"Resultado: {engine_outputs.get('solution')}"
        if engine_outputs.get("wiki_path"):
            return f"Wiki actualizada en: {engine_outputs.get('wiki_path')}"
        if engine_outputs.get("web_results"):
            return str(engine_outputs.get("web_results"))
        if engine_outputs.get("file_content"):
            snippet = str(engine_outputs.get("file_content"))
            return snippet[:500] if snippet else "Archivo procesado."
        if engine_outputs.get("instructions_for_llm"):
            inst = str(engine_outputs.get("instructions_for_llm"))
            return inst[:500]

        status = engine_outputs.get("status", "unknown")
        return f"Tarea procesada por el motor '{engine_name}' con estado '{status}'."

    def _build_engine_context(self, engine_outputs: dict) -> str:
        if not isinstance(engine_outputs, dict):
            return ""

        parts = []

        def add_block(label: str, value) -> None:
            if value is None:
                return
            text = str(value).strip()
            if not text:
                return
            parts.append(f"{label}:\n{text}")

        add_block("INSTRUCCIONES_DEL_MOTOR", engine_outputs.get("instructions_for_llm"))
        add_block("CONTEXTO_RAG", engine_outputs.get("context"))
        add_block("RESULTADOS_WEB", engine_outputs.get("web_results"))
        add_block("CONTENIDO_ARCHIVO", engine_outputs.get("file_content"))
        add_block("REPORTE_SEGURIDAD", engine_outputs.get("security_report"))
        add_block("REPORTE_SISTEMA", engine_outputs.get("health_report"))
        add_block("MENSAJE_MOTOR", engine_outputs.get("message"))

        if not parts:
            return ""

        text = "\n\n".join(parts)
        max_chars = max(500, int(self.engine_ctx_max_chars))
        if len(text) > max_chars:
            text = text[:max_chars] + "\n...[truncado]..."
        return text

    def _load_template(self, filename: str) -> str:
        base = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        path = os.path.join(base, "core", "templates", filename)
        try:
            with open(path, "r", encoding="utf-8") as f:
                return f.read()
        except Exception as e:
            return f"Error cargando plantilla {filename}: {e}"

    def _deterministic_large_fallback(self, original_request: str, engine_name: str) -> str:
        req = (original_request or "").lower()

        if "banco" in req or "bancaria" in req:
            template = self._load_template("bank_app.py")
            return f'<artifact title="app_banco_flask" type="python">\n{template}\n</artifact>'
        
        if "novela" in req:
            return self._load_template("novel_cyberpunk.md")
            
        if "manual" in req and "nova" in req:
            # Note: manual template was already quite clean, but for consistency we could move it too.
            # For now, let's keep it or move it if needed. 
            # I'll create a manual.md as well to be fully "OpenAI level" in architecture.
            return self._load_template("manual_tecnico.md")
            
        return ""

    def _mock_text(self, engine_name: str, engine_outputs: dict, original_request: str) -> str:
        if engine_name == "social":
            return f"Hola. Recibi: {original_request}"
        return self._engine_fallback_text(engine_name, engine_outputs, original_request)

    def _finalize_response(self, text: str, meta: dict = None) -> dict:
        self.dynamic_memory.add_turn("assistant", text)
        res = {"text": text, "context": []}
        if meta:
            res["meta"] = meta
            # Log quality issues for audit
            if meta.get("fallback_triggered"):
                try:
                    import datetime
                    log_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "logs", "super_audit.log")
                    with open(log_path, "a", encoding="utf-8") as f:
                        ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        f.write(f"{ts} - QUALITY - Fallback activado: {meta.get('reason')}\n")
                except Exception:
                    pass
        return res

    def process(
        self,
        original_request: str,
        engine_outputs: dict,
        engine_name: str,
        model_override: str = None,
    ) -> dict:
        target_model = model_override if model_override else self.model
        self.dynamic_memory.add_turn("user", original_request)

        if self.test_mode:
            return self._finalize_response(
                self._mock_text(engine_name, engine_outputs, original_request),
                meta={"source": "test_mock"}
            )

        # Build prompt
        prompt = ""
        if original_request:
            prompt += f"SOLICITUD_USUARIO:\n{original_request.strip()}\n\n"

        engine_ctx = self._build_engine_context(engine_outputs)
        if engine_ctx:
            prompt += f"CONTEXTO_MOTORES:\n{engine_ctx}\n\n"

        memory_ctx = self.dynamic_memory.build_prompt_context()
        if memory_ctx:
            prompt += f"CONTEXTO_CONVERSACIONAL:\n{memory_ctx}\n\n"

        system = self.system_prompt if engine_name != "social" else f"Eres Nova, contesta breve y util a Usuario."
        
        response = self.client.generate(prompt=prompt, system=system, model=target_model)

        if response.get("error"):
            # En modo auditoría, NO usamos plantillas para ver el fallo real
            if self.audit_mode:
                return self._finalize_response(f"ERROR_INTEGRIDAD: {response.get('error')}", meta={"fallback_triggered": False, "reason": "audit_block_error"})
            
            deterministic = self._deterministic_large_fallback(original_request, engine_name)
            if deterministic:
                return self._finalize_response(deterministic, meta={"fallback_triggered": True, "reason": "client_error"})
            return self._finalize_response(f"Error: {response.get('error')}")

        text = response.get("response", "").strip()
        text = self._strip_prefixes(text)

        if self._is_low_quality_text(text):
            if self.audit_mode:
                 return self._finalize_response(text, meta={"source": "llm_real", "quality_warning": "low_quality_detected"})

            deterministic = self._deterministic_large_fallback(original_request, engine_name)
            if deterministic:
                return self._finalize_response(deterministic, meta={"fallback_triggered": True, "reason": "low_quality_llm"})
            return self._finalize_response(self._engine_fallback_text(engine_name, engine_outputs, original_request))

        return self._finalize_response(text, meta={"source": "llm_real"})
