import json
import os
import random
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FuturesTimeoutError
from typing import Dict, Any, List, Optional

import requests
import yaml


class OllamaClient:
    """
    Compat client name kept for backward compatibility.
    Backend now supports local GGUF via llama-cpp-python (default) and Ollama (optional).
    """

    def __init__(
        self,
        base_url: str = "http://localhost:11434",
        default_model: str = "local-gguf",
        request_timeout: int = 30,
    ):
        self.base_url = base_url
        self.default_model = default_model
        self.request_timeout = request_timeout
        self._llama = None
        self._local_backend = None
        self._mock_dataset = []

        self.project_root = os.path.dirname(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        )
        self.backend = "llama_cpp"
        self.temperature = 0.4
        self.n_ctx = 512
        self.n_threads = max(1, (os.cpu_count() or 2) // 2)
        self.n_batch = 128
        self.n_gpu_layers = 0
        self.max_tokens = 64
        self.model_type = "llama"
        self.local_runtime = "auto"
        self.mock_mode = False
        self.auto_mock_on_timeout = True
        self.real_response_timeout_sec = 20
        self.mock_dataset_path = os.path.join(
            self.project_root, "knowledge", "datasets", "logic_core.json"
        )
        self.model_path = os.path.join(
            self.project_root,
            "models",
            "tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf",
        )

        self._load_llm_config()

    def _load_llm_config(self) -> None:
        config_path = os.path.join(self.project_root, "config.yaml")
        if not os.path.exists(config_path):
            return

        try:
            with open(config_path, "r", encoding="utf-8") as f:
                cfg = yaml.safe_load(f) or {}
            llm = cfg.get("llm", {})
            self.backend = str(llm.get("backend", self.backend)).lower()
            self.temperature = float(llm.get("temperature", self.temperature))
            self.n_ctx = int(llm.get("context_window", self.n_ctx))
            self.n_threads = int(llm.get("n_threads", self.n_threads))
            self.n_batch = int(llm.get("n_batch", self.n_batch))
            self.n_gpu_layers = int(llm.get("n_gpu_layers", self.n_gpu_layers))
            self.max_tokens = int(llm.get("max_tokens", self.max_tokens))
            self.model_type = str(llm.get("model_type", self.model_type))
            self.local_runtime = str(llm.get("local_runtime", self.local_runtime)).lower()
            self.mock_mode = bool(llm.get("mock_mode", self.mock_mode))
            self.auto_mock_on_timeout = bool(llm.get("auto_mock_on_timeout", self.auto_mock_on_timeout))
            self.real_response_timeout_sec = int(llm.get("real_response_timeout_sec", self.real_response_timeout_sec))
            mock_path = llm.get("mock_dataset_path")
            if mock_path:
                self.mock_dataset_path = mock_path if os.path.isabs(mock_path) else os.path.join(self.project_root, mock_path)
            if self.mock_mode:
                self._load_mock_dataset(self.mock_dataset_path)
            cfg_model_path = llm.get("model_path")
            if cfg_model_path:
                self.model_path = cfg_model_path
                if not os.path.isabs(self.model_path):
                    self.model_path = os.path.join(self.project_root, self.model_path)

            host = llm.get("host")
            if host:
                self.base_url = host
        except Exception:
            # Keep safe defaults if config is malformed.
            pass

    def _load_mock_dataset(self, path: str) -> None:
        if not path or not os.path.exists(path):
            self._mock_dataset = []
            return

        try:
            with open(path, "r", encoding="utf-8") as f:
                entries = json.load(f)
            if isinstance(entries, list):
                self._mock_dataset = [
                    e for e in entries if isinstance(e, dict) and e.get("output")
                ]
            else:
                self._mock_dataset = []
        except Exception:
            self._mock_dataset = []

    def _ensure_local_model(self) -> None:
        if self._llama is not None:
            return

        if self.local_runtime in {"disabled", "none", "off"}:
            raise RuntimeError(
                "Runtime local deshabilitado (CPU sin AVX o modo ahorro)."
            )

        if not os.path.exists(self.model_path):
            raise FileNotFoundError(
                f"No se encontro el modelo GGUF en: {self.model_path}. "
                "Ejecuta setup_nova.bat para descargarlo."
            )

        def try_llama_cpp():
            from llama_cpp import Llama
            return Llama(
                model_path=self.model_path,
                n_ctx=self.n_ctx,
                n_threads=self.n_threads,
                n_batch=self.n_batch,
                n_gpu_layers=self.n_gpu_layers,
                verbose=False,
            )

        def try_ctransformers():
            from ctransformers import AutoModelForCausalLM
            return AutoModelForCausalLM.from_pretrained(
                self.project_root,
                model_file=self.model_path,
                model_type=self.model_type,
                gpu_layers=0,
                threads=self.n_threads,
                context_length=self.n_ctx,
            )

        errors = []

        order = []
        if self.local_runtime == "ctransformers":
            order = [("ctransformers", try_ctransformers), ("llama_cpp", try_llama_cpp)]
        elif self.local_runtime == "llama_cpp":
            order = [("llama_cpp", try_llama_cpp), ("ctransformers", try_ctransformers)]
        else:
            order = [("llama_cpp", try_llama_cpp), ("ctransformers", try_ctransformers)]

        for backend_name, loader in order:
            try:
                self._llama = loader()
                self._local_backend = backend_name
                return
            except Exception as e:
                errors.append(f"{backend_name}: {e}")

        raise RuntimeError("No se pudo inicializar backend local. " + " | ".join(errors))

    def _generate_local(
        self,
        prompt: str,
        system: str = "",
        stream: bool = False,
    ) -> Dict[str, Any]:
        if stream:
            return {
                "error": "stream=True no soportado en backend local llama_cpp",
                "response": "",
            }

        self._ensure_local_model()
        if self._local_backend == "llama_cpp":
            messages = []
            if system:
                messages.append({"role": "system", "content": system})
            messages.append({"role": "user", "content": prompt})

            raw = self._llama.create_chat_completion(
                messages=messages,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
            )
            choices = raw.get("choices", [])
            if not choices:
                return {"error": "Respuesta vacia de llama_cpp", "response": ""}

            message = choices[0].get("message", {})
            content = message.get("content", "")
            return {"response": content, "done": True}

        if self._local_backend == "ctransformers":
            prompt_parts = []
            if system:
                prompt_parts.append(f"Instrucciones del sistema:\n{system}\n")
            prompt_parts.append(f"Usuario:\n{prompt}\n")
            prompt_parts.append("Asistente:\n")
            full_prompt = "\n".join(prompt_parts)
            text = self._llama(
                full_prompt,
                max_new_tokens=self.max_tokens,
                temperature=self.temperature,
            )
            return {"response": str(text), "done": True}

        return {"error": "Backend local no inicializado", "response": ""}

    def _generate_ollama(
        self,
        prompt: str,
        system: str = "",
        model: Optional[str] = None,
        stream: bool = False,
    ) -> Dict[str, Any]:
        target_model = model if model else self.default_model
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        url = f"{self.base_url}/api/chat"
        payload = {
            "model": target_model,
            "messages": messages,
            "stream": stream,
            "options": {
                "temperature": self.temperature,
                "num_ctx": self.n_ctx,
            },
        }

        effective_timeout = self.request_timeout
        if self.auto_mock_on_timeout:
            effective_timeout = min(self.request_timeout, self.real_response_timeout_sec)

        response = requests.post(
            url, json=payload, stream=stream, timeout=effective_timeout
        )
        response.raise_for_status()
        if stream:
            return response
        raw_json = response.json()
        if "message" in raw_json:
            return {
                "response": raw_json["message"].get("content", ""),
                "done": raw_json.get("done", True),
            }
        return raw_json

    def _run_backend_request(
        self,
        prompt: str,
        system: str,
        model: Optional[str],
        stream: bool,
    ) -> Dict[str, Any]:
        if self.backend == "llama_cpp":
            return self._generate_local(prompt=prompt, system=system, stream=stream)
        return self._generate_ollama(
            prompt=prompt,
            system=system,
            model=model,
            stream=stream,
        )

    def _run_with_worker_timeout(
        self,
        prompt: str,
        system: str,
        model: Optional[str],
        stream: bool,
        timeout_sec: int,
    ) -> Dict[str, Any]:
        """
        Execute backend inference in a worker thread to keep Nova's main thread responsive.
        """
        executor = ThreadPoolExecutor(max_workers=1, thread_name_prefix="nova_llm_worker")
        future = executor.submit(
            self._run_backend_request,
            prompt,
            system,
            model,
            stream,
        )
        try:
            return {"status": "ok", "result": future.result(timeout=max(1, int(timeout_sec)))}
        except FuturesTimeoutError:
            future.cancel()
            return {"status": "timeout", "error": f"timeout>{timeout_sec}s"}
        except Exception as e:
            return {"status": "error", "error": str(e)}
        finally:
            executor.shutdown(wait=False, cancel_futures=True)

    def generate(
        self,
        prompt: str,
        system: str = "",
        context: List[Any] = [],
        model: Optional[str] = None,
        stream: bool = False,
    ) -> Dict[str, Any]:
        _ = context  # kept for compatibility

        if self.mock_mode:
            return self._generate_mock(prompt, reason="forced")

        timeout_budget = self.real_response_timeout_sec if self.auto_mock_on_timeout else self.request_timeout
        worker_result = self._run_with_worker_timeout(
            prompt=prompt,
            system=system,
            model=model,
            stream=stream,
            timeout_sec=timeout_budget,
        )

        if worker_result.get("status") == "ok":
            return worker_result.get("result", {"response": "", "done": True})

        if worker_result.get("status") == "timeout":
            # Log for industrial audit
            try:
                log_path = os.path.join(self.project_root, "logs", "super_audit.log")
                with open(log_path, "a", encoding="utf-8") as f:
                    import datetime
                    ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    f.write(f"{ts} - ERROR - TIMEOUT LLM ({timeout_budget}s) - Activando Mock Mode.\n")
            except:
                pass
                
            if self.auto_mock_on_timeout:
                self.mock_mode = True
                return self._generate_mock(prompt, reason=f"timeout({timeout_budget}s)")
            return {"error": "timeout", "response": ""}

        err = str(worker_result.get("error", "unknown backend error"))
        if "timeout" in err.lower() and self.auto_mock_on_timeout:
            self.mock_mode = True
            return self._generate_mock(prompt, reason="timeout")
        return {"error": err, "response": ""}

    def _generate_mock(self, prompt: str, reason: str = "manual") -> Dict[str, Any]:
        """Returns a synthetic response for environments without LLM hardware support."""
        if not self._mock_dataset:
            self._load_mock_dataset(self.mock_dataset_path)
        if not self._mock_dataset:
            return {
                "response": "[MOCK MODE] No hay datos de conocimiento compatibles. Ejecuta `nightly_ascension.py` para regenerarlos.",
                "done": True,
            }

        entry = random.choice(self._mock_dataset)
        output = entry.get("output", "Entendido.")
        return {"response": f"[MOCK MODE | {reason}] {output}", "done": True}
