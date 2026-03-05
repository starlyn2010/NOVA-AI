"""
Nova Notion Connector — Production v2.8.0
===========================================
Create pages, databases, take notes via Notion API.
"""

from .base import BaseConnector


class NotionConnector(BaseConnector):
    NAME = "notion"
    REQUIRED_KEYS = ["api_key"]
    API_BASE = "https://api.notion.com/v1"
    NOTION_VERSION = "2022-06-28"

    def _headers(self):
        return {
            "Authorization": f"Bearer {self._cfg('api_key')}",
            "Content-Type": "application/json",
            "Notion-Version": self.NOTION_VERSION,
        }

    def search(self, query: str) -> dict:
        """Search Notion workspace."""
        if not self._cfg("api_key"):
            return self._warn(
                "Notion no configurado. Obtén tu API key en https://www.notion.so/my-integrations",
                instructions_for_llm="El usuario necesita crear una integración en Notion y copiar el token.",
            )
        try:
            import requests
            r = requests.post(
                f"{self.API_BASE}/search",
                headers=self._headers(),
                json={"query": query, "page_size": 10},
                timeout=10,
            )
            r.raise_for_status()
            results = [
                {
                    "id": item["id"],
                    "type": item["object"],
                    "title": self._extract_title(item),
                    "url": item.get("url", ""),
                }
                for item in r.json().get("results", [])
            ]
            return self._ok(f"{len(results)} resultados en Notion.", results=results)
        except Exception as e:
            return self._err(f"Error: {e}")

    def create_page(self, parent_id: str, title: str, content: str = "") -> dict:
        """Create a new page in Notion."""
        if not self._cfg("api_key"):
            return self._warn("Notion no configurado.")
        try:
            import requests
            children = []
            if content:
                for paragraph in content.split("\n"):
                    if paragraph.strip():
                        children.append({
                            "object": "block",
                            "type": "paragraph",
                            "paragraph": {
                                "rich_text": [{"type": "text", "text": {"content": paragraph.strip()}}]
                            },
                        })

            payload = {
                "parent": {"page_id": parent_id},
                "properties": {
                    "title": [{"text": {"content": title}}],
                },
                "children": children,
            }

            r = requests.post(
                f"{self.API_BASE}/pages",
                headers=self._headers(),
                json=payload,
                timeout=15,
            )
            r.raise_for_status()
            page = r.json()
            return self._ok(
                f"Página '{title}' creada en Notion.",
                page_id=page["id"],
                url=page.get("url", ""),
                instructions_for_llm=f"Página creada: {page.get('url', page['id'])}",
            )
        except Exception as e:
            return self._err(f"Error: {e}")

    def append_block(self, page_id: str, content: str) -> dict:
        """Append content to an existing Notion page."""
        if not self._cfg("api_key"):
            return self._warn("Notion no configurado.")
        try:
            import requests
            children = [
                {
                    "object": "block",
                    "type": "paragraph",
                    "paragraph": {
                        "rich_text": [{"type": "text", "text": {"content": content}}]
                    },
                }
            ]
            r = requests.patch(
                f"{self.API_BASE}/blocks/{page_id}/children",
                headers=self._headers(),
                json={"children": children},
                timeout=10,
            )
            r.raise_for_status()
            return self._ok("Contenido añadido a la página de Notion.")
        except Exception as e:
            return self._err(f"Error: {e}")

    @staticmethod
    def _extract_title(item: dict) -> str:
        props = item.get("properties", {})
        for key in props:
            prop = props[key]
            if prop.get("type") == "title":
                titles = prop.get("title", [])
                if titles:
                    return titles[0].get("text", {}).get("content", "Sin título")
        return "Sin título"

    def _execute(self, request: str) -> dict:
        req = request.strip().lower()
        if "buscar" in req or "search" in req:
            return self.search(request)
        return self.search(request)
