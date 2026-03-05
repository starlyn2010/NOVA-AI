"""
Nova Pixazo Connector — Production v2.8.0
==========================================
AI Image Generation via Pixazo API.
Supports multiple models: Flux Schnell, Stable Diffusion, SDXL.
Free tier: 100 API calls with no credit card.
"""

import os
import base64
import datetime
from .base import BaseConnector


class PixazoConnector(BaseConnector):
    NAME = "pixazo"
    REQUIRED_KEYS = ["api_key"]
    API_BASE = "https://api.pixazo.ai/v1"

    MODELS = {
        "flux": {"name": "Flux Schnell", "tier": "free", "best_for": "Arte rápido y conceptual"},
        "sd": {"name": "Stable Diffusion", "tier": "free", "best_for": "Versatilidad general"},
        "sdxl": {"name": "Stable Diffusion XL", "tier": "free", "best_for": "Alta resolución 1024x1024+"},
        "dalle3": {"name": "DALL·E 3", "tier": "pro", "best_for": "Fotorrealismo + texto en imágenes"},
        "ideogram": {"name": "Ideogram", "tier": "pro", "best_for": "Logos y texto artístico"},
    }

    def __init__(self):
        super().__init__()
        self._root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self._output_dir = os.path.join(self._root, "data", "generated_images")
        os.makedirs(self._output_dir, exist_ok=True)
        self._usage_count = 0
        self._max_free = 100

    def list_models(self, free_only: bool = True) -> dict:
        """List available image generation models."""
        models = {}
        for key, info in self.MODELS.items():
            if free_only and info["tier"] != "free":
                continue
            models[key] = info
        return self._ok("Modelos disponibles", models=models)

    def generate_image(
        self,
        prompt: str,
        model: str = "flux",
        width: int = 1024,
        height: int = 1024,
        style: str = "auto",
    ) -> dict:
        """Generate an image from a text prompt."""
        api_key = self._cfg("api_key")
        if not api_key:
            return self._warn(
                "Pixazo no configurado. Añade api_key en config.yaml → connectors → pixazo. "
                "Obtén tu key gratis en https://pixazo.ai",
                instructions_for_llm="Dile al usuario que necesita registrarse en pixazo.ai para obtener una API key gratis.",
            )

        if self._usage_count >= self._max_free:
            return self._warn(
                f"Has alcanzado el límite de {self._max_free} imágenes gratuitas. "
                "Considera actualizar tu plan en pixazo.ai",
                instructions_for_llm="Informa al usuario que se agotaron sus créditos gratuitos de Pixazo.",
            )

        # Validate model
        if model not in self.MODELS:
            model = "flux"

        model_info = self.MODELS[model]
        if model_info["tier"] != "free" and not self._cfg("pro_plan"):
            return self._warn(
                f"El modelo '{model_info['name']}' requiere plan Pro. "
                f"Modelos gratuitos disponibles: {', '.join(k for k,v in self.MODELS.items() if v['tier']=='free')}"
            )

        try:
            import requests

            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            }
            payload = {
                "prompt": prompt,
                "model": model,
                "width": width,
                "height": height,
                "style": style,
                "num_images": 1,
            }

            response = requests.post(
                f"{self.API_BASE}/generate",
                headers=headers,
                json=payload,
                timeout=60,
            )
            response.raise_for_status()
            data = response.json()

            # Save the image
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"nova_img_{timestamp}_{model}.png"
            filepath = os.path.join(self._output_dir, filename)

            # Handle different response formats
            if "images" in data and data["images"]:
                img_data = data["images"][0]
                if isinstance(img_data, str) and img_data.startswith("http"):
                    # URL response — download it
                    img_response = requests.get(img_data, timeout=30)
                    with open(filepath, "wb") as f:
                        f.write(img_response.content)
                elif isinstance(img_data, str):
                    # Base64 response
                    with open(filepath, "wb") as f:
                        f.write(base64.b64decode(img_data))
                elif isinstance(img_data, dict) and "url" in img_data:
                    img_response = requests.get(img_data["url"], timeout=30)
                    with open(filepath, "wb") as f:
                        f.write(img_response.content)
            elif "url" in data:
                img_response = requests.get(data["url"], timeout=30)
                with open(filepath, "wb") as f:
                    f.write(img_response.content)
            else:
                return self._err("Formato de respuesta inesperado de Pixazo.")

            self._usage_count += 1
            remaining = self._max_free - self._usage_count

            return self._ok(
                f"Imagen generada con {model_info['name']}",
                filepath=filepath,
                model=model,
                model_name=model_info["name"],
                remaining_free=remaining,
                prompt=prompt,
                instructions_for_llm=(
                    f"Imagen creada exitosamente en: {filepath}. "
                    f"Modelo usado: {model_info['name']}. "
                    f"Créditos gratuitos restantes: {remaining}/{self._max_free}."
                ),
            )

        except Exception as e:
            return self._err(f"Error generando imagen: {e}")

    # ── Unified Contract ────────────────────────────────────────────
    def _execute(self, request: str) -> dict:
        """Parse image generation request."""
        req = request.strip().lower()

        # Model selection from request
        model = "flux"
        for key in self.MODELS:
            if key in req:
                model = key
                break

        return self.generate_image(prompt=request, model=model)
