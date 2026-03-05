"""
Nova Canva Connector — Production v2.8.0
==========================================
Professional design creation via Canva API.
Supports templates, text insertion, image upload, and export.
"""

import os
import datetime
from .base import BaseConnector


class CanvaConnector(BaseConnector):
    NAME = "canva"
    REQUIRED_KEYS = ["api_key"]
    API_BASE = "https://api.canva.com/rest/v1"

    TEMPLATE_CATEGORIES = {
        "instagram_post": {"name": "Post de Instagram", "width": 1080, "height": 1080},
        "facebook_post": {"name": "Post de Facebook", "width": 1200, "height": 630},
        "youtube_thumbnail": {"name": "Thumbnail YouTube", "width": 1280, "height": 720},
        "presentation": {"name": "Presentación", "width": 1920, "height": 1080},
        "business_card": {"name": "Tarjeta de Visita", "width": 1050, "height": 600},
        "flyer": {"name": "Flyer A4", "width": 2480, "height": 3508},
        "logo": {"name": "Logo", "width": 500, "height": 500},
        "banner_web": {"name": "Banner Web", "width": 1920, "height": 480},
        "story": {"name": "Historia/Story", "width": 1080, "height": 1920},
        "poster": {"name": "Póster", "width": 1587, "height": 2245},
    }

    def __init__(self):
        super().__init__()
        self._root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self._output_dir = os.path.join(self._root, "data", "designs")
        os.makedirs(self._output_dir, exist_ok=True)

    def list_templates(self) -> dict:
        """List available design template categories."""
        return self._ok(
            "Plantillas disponibles",
            templates=self.TEMPLATE_CATEGORIES,
            instructions_for_llm=(
                "Canva soporta estos tipos de diseño: "
                + ", ".join(f"{v['name']} ({k})" for k, v in self.TEMPLATE_CATEGORIES.items())
            ),
        )

    def create_design(
        self,
        title: str,
        template_type: str = "instagram_post",
        text_elements: list = None,
        brand_colors: list = None,
    ) -> dict:
        """
        Create a new design in Canva.
        text_elements: [{"text": "Titulo", "position": "top"}, ...]
        brand_colors: ["#FF5733", "#2E86AB"]
        """
        api_key = self._cfg("api_key")
        if not api_key:
            return self._warn(
                "Canva no configurado. Obtén tu API key gratis en https://www.canva.com/developers/",
                instructions_for_llm=(
                    "Indica al usuario que necesita registrarse como desarrollador en Canva "
                    "y obtener una API key para crear diseños automáticamente."
                ),
            )

        template = self.TEMPLATE_CATEGORIES.get(template_type, self.TEMPLATE_CATEGORIES["instagram_post"])

        try:
            import requests

            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            }

            # Create design
            payload = {
                "design_type": {
                    "width": template["width"],
                    "height": template["height"],
                },
                "title": title,
                "asset_types": ["image"],
            }

            response = requests.post(
                f"{self.API_BASE}/designs",
                headers=headers,
                json=payload,
                timeout=30,
            )

            if response.status_code == 200:
                data = response.json()
                design_id = data.get("design", {}).get("id", "")
                edit_url = data.get("design", {}).get("urls", {}).get("edit_url", "")

                return self._ok(
                    f"Diseño '{title}' creado ({template['name']})",
                    design_id=design_id,
                    edit_url=edit_url,
                    template_type=template_type,
                    dimensions=f"{template['width']}x{template['height']}",
                    instructions_for_llm=(
                        f"Diseño creado exitosamente. ID: {design_id}. "
                        f"El usuario puede editarlo en: {edit_url}. "
                        f"Tipo: {template['name']} ({template['width']}x{template['height']}px)."
                    ),
                )
            else:
                return self._err(f"Error de Canva API: {response.status_code} — {response.text}")

        except ImportError:
            return self._err("requests no instalado.")
        except Exception as e:
            return self._err(f"Error creando diseño: {e}")

    def search_templates(self, query: str) -> dict:
        """Search for Canva templates by keyword."""
        api_key = self._cfg("api_key")
        if not api_key:
            return self._warn("Canva no configurado.")

        try:
            import requests

            headers = {"Authorization": f"Bearer {api_key}"}
            params = {"query": query, "limit": 10}

            response = requests.get(
                f"{self.API_BASE}/brand-templates",
                headers=headers,
                params=params,
                timeout=15,
            )

            if response.status_code == 200:
                data = response.json()
                templates = data.get("items", [])
                return self._ok(
                    f"{len(templates)} plantillas encontradas para '{query}'",
                    templates=[
                        {"id": t.get("id"), "title": t.get("title"), "thumbnail": t.get("thumbnail", {}).get("url")}
                        for t in templates
                    ],
                )
            return self._err(f"Error buscando plantillas: {response.text}")

        except Exception as e:
            return self._err(f"Error: {e}")

    def export_design(self, design_id: str, format: str = "png") -> dict:
        """Export a Canva design to file."""
        api_key = self._cfg("api_key")
        if not api_key:
            return self._warn("Canva no configurado.")

        try:
            import requests

            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            }
            payload = {"format_type": format.upper()}

            response = requests.post(
                f"{self.API_BASE}/designs/{design_id}/exports",
                headers=headers,
                json=payload,
                timeout=30,
            )

            if response.status_code == 200:
                data = response.json()
                export_url = data.get("export", {}).get("urls", [{}])[0].get("url", "")

                if export_url:
                    # Download the exported file
                    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                    filename = f"design_{timestamp}.{format}"
                    filepath = os.path.join(self._output_dir, filename)

                    img_data = requests.get(export_url, timeout=30)
                    with open(filepath, "wb") as f:
                        f.write(img_data.content)

                    return self._ok(
                        f"Diseño exportado: {filepath}",
                        filepath=filepath,
                        format=format,
                    )

            return self._err(f"Error exportando: {response.text}")

        except Exception as e:
            return self._err(f"Error: {e}")

    # ── Unified Contract ────────────────────────────────────────────
    def _execute(self, request: str) -> dict:
        req = request.strip().lower()

        if "plantilla" in req or "template" in req:
            if "listar" in req or "buscar" in req:
                return self.search_templates(request)
            return self.list_templates()

        if "exportar" in req or "descargar" in req:
            parts = request.strip().split()
            for p in parts:
                if len(p) > 10 and not p.startswith(("exportar", "descargar")):
                    return self.export_design(p)

        # Default: try to create a design
        template_type = "instagram_post"
        for key in self.TEMPLATE_CATEGORIES:
            if key.replace("_", " ") in req or key in req:
                template_type = key
                break

        # FALLBACK: If API key is missing, use Smart Browser (Visual Mode)
        # We return a special instruction that the Orchestrator (Hyper-Router) can pick up.
        return self._warn(
            "Modo API de Canva no configurado. Intentando modo Visual (Navegador).",
            instructions_for_llm=(
                f"El usuario quiere crear un diseño '{template_type}' en Canva pero no hay API Key. "
                "USA LA HERRAMIENTA 'crawl' (Navegador Inteligente) para esto. "
                f"Ordena al navegador: 'Ir a canva.com, iniciar sesión si es necesario, y crear un nuevo diseño de tipo {template_type}'."
            )
        )
