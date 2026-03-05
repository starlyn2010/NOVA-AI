"""
Nova Wolfram Alpha Connector — Production v2.8.0
==================================================
Advanced math, science, and knowledge queries via Wolfram API.
Free: 2000 queries/month.
"""

from .base import BaseConnector


class WolframConnector(BaseConnector):
    NAME = "wolfram"
    REQUIRED_KEYS = ["app_id"]
    API_BASE = "https://api.wolframalpha.com/v2"

    def query(self, question: str) -> dict:
        """Full result query to Wolfram Alpha."""
        app_id = self._cfg("app_id")
        if not app_id:
            return self._warn(
                "Wolfram Alpha no configurado. Obtén tu AppID gratis en https://developer.wolframalpha.com",
                instructions_for_llm=(
                    "Para activar Wolfram Alpha, el usuario necesita registrarse en "
                    "developer.wolframalpha.com, crear una app y copiar el AppID."
                ),
            )

        try:
            import requests
            r = requests.get(
                f"{self.API_BASE}/query",
                params={
                    "input": question,
                    "appid": app_id,
                    "format": "plaintext",
                    "output": "json",
                },
                timeout=15,
            )
            r.raise_for_status()
            data = r.json()

            pods = data.get("queryresult", {}).get("pods", [])
            results = []
            for pod in pods:
                title = pod.get("title", "")
                subpods = pod.get("subpods", [])
                for sub in subpods:
                    text = sub.get("plaintext", "")
                    if text:
                        results.append({"title": title, "result": text})

            if results:
                answer = "\n".join(f"**{r['title']}**: {r['result']}" for r in results[:5])
                return self._ok(
                    f"Wolfram Alpha respondió a: {question}",
                    results=results[:5],
                    answer=answer,
                    instructions_for_llm=f"Resultado de Wolfram Alpha para '{question}':\n{answer}",
                )
            return self._warn("Wolfram no encontró resultados para esa consulta.")

        except Exception as e:
            return self._err(f"Error Wolfram: {e}")

    def short_answer(self, question: str) -> dict:
        """Quick short-answer query."""
        app_id = self._cfg("app_id")
        if not app_id:
            return self._warn("Wolfram Alpha no configurado.")

        try:
            import requests
            r = requests.get(
                "https://api.wolframalpha.com/v1/result",
                params={"input": question, "appid": app_id},
                timeout=10,
            )
            if r.status_code == 200:
                return self._ok(r.text, answer=r.text)
            return self._err("Sin respuesta corta disponible.")
        except Exception as e:
            return self._err(f"Error: {e}")

    def _execute(self, request: str) -> dict:
        return self.query(request)


class TrelloConnector(BaseConnector):
    """Trello integration for project management."""
    NAME = "trello"
    REQUIRED_KEYS = ["api_key", "token"]
    API_BASE = "https://api.trello.com/1"

    def _params(self):
        return {"key": self._cfg("api_key"), "token": self._cfg("token")}

    def list_boards(self) -> dict:
        if not self._cfg("api_key"):
            return self._warn(
                "Trello no configurado. Obtén tu key en https://trello.com/power-ups/admin",
                instructions_for_llm="El usuario necesita obtener API key y token de Trello.",
            )
        try:
            import requests
            r = requests.get(
                f"{self.API_BASE}/members/me/boards",
                params=self._params(),
                timeout=10,
            )
            r.raise_for_status()
            boards = [{"id": b["id"], "name": b["name"], "url": b["url"]} for b in r.json()]
            return self._ok(f"{len(boards)} tableros encontrados.", boards=boards)
        except Exception as e:
            return self._err(f"Error Trello: {e}")

    def create_card(self, list_id: str, name: str, description: str = "") -> dict:
        if not self._cfg("api_key"):
            return self._warn("Trello no configurado.")
        try:
            import requests
            params = {**self._params(), "name": name, "desc": description, "idList": list_id}
            r = requests.post(f"{self.API_BASE}/cards", params=params, timeout=10)
            r.raise_for_status()
            card = r.json()
            return self._ok(f"Tarjeta creada: {name}", card_id=card["id"], url=card["url"])
        except Exception as e:
            return self._err(f"Error: {e}")

    def _execute(self, request: str) -> dict:
        return self.list_boards()


class VercelConnector(BaseConnector):
    """Vercel deployment connector."""
    NAME = "vercel"
    REQUIRED_KEYS = ["token"]
    API_BASE = "https://api.vercel.com"

    def _headers(self):
        return {"Authorization": f"Bearer {self._cfg('token')}"}

    def list_projects(self) -> dict:
        if not self._cfg("token"):
            return self._warn("Vercel no configurado. Token en https://vercel.com/account/tokens")
        try:
            import requests
            r = requests.get(f"{self.API_BASE}/v9/projects", headers=self._headers(), timeout=10)
            r.raise_for_status()
            projects = [
                {"name": p["name"], "id": p["id"], "url": f"https://{p.get('alias', [{}])[0].get('domain', p['name']+'.vercel.app')}"}
                for p in r.json().get("projects", [])
            ]
            return self._ok(f"{len(projects)} proyectos.", projects=projects)
        except Exception as e:
            return self._err(f"Error: {e}")

    def list_deployments(self, limit: int = 5) -> dict:
        if not self._cfg("token"):
            return self._warn("Vercel no configurado.")
        try:
            import requests
            r = requests.get(
                f"{self.API_BASE}/v6/deployments",
                headers=self._headers(),
                params={"limit": limit},
                timeout=10,
            )
            r.raise_for_status()
            deps = [
                {
                    "name": d.get("name"),
                    "url": f"https://{d.get('url', '')}",
                    "state": d.get("readyState", d.get("state")),
                    "created": d.get("created"),
                }
                for d in r.json().get("deployments", [])
            ]
            return self._ok(f"{len(deps)} deployments.", deployments=deps)
        except Exception as e:
            return self._err(f"Error: {e}")

    def _execute(self, request: str) -> dict:
        req = request.strip().lower()
        if "deploy" in req:
            return self.list_deployments()
        return self.list_projects()
