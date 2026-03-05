"""
Nova GitHub Connector — Production v2.8.0
===========================================
Manage repos, issues, PRs via GitHub API.
"""

import os
import json
from .base import BaseConnector


class GitHubConnector(BaseConnector):
    NAME = "github"
    REQUIRED_KEYS = ["token"]
    API_BASE = "https://api.github.com"

    def __init__(self):
        super().__init__()

    def _headers(self):
        token = self._cfg("token")
        return {
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github.v3+json",
        }

    def get_user(self) -> dict:
        """Get authenticated user info."""
        if not self._cfg("token"):
            return self._warn("GitHub no configurado. Añade token en config.yaml → connectors → github")
        try:
            import requests
            r = requests.get(f"{self.API_BASE}/user", headers=self._headers(), timeout=10)
            r.raise_for_status()
            user = r.json()
            return self._ok(
                f"Autenticado como: {user['login']}",
                username=user["login"],
                name=user.get("name"),
                repos=user.get("public_repos"),
                avatar=user.get("avatar_url"),
            )
        except Exception as e:
            return self._err(f"Error GitHub: {e}")

    def list_repos(self, limit: int = 10) -> dict:
        """List user's repos."""
        if not self._cfg("token"):
            return self._warn("GitHub no configurado.")
        try:
            import requests
            r = requests.get(
                f"{self.API_BASE}/user/repos",
                headers=self._headers(),
                params={"sort": "updated", "per_page": limit},
                timeout=10,
            )
            r.raise_for_status()
            repos = [
                {
                    "name": repo["name"],
                    "full_name": repo["full_name"],
                    "description": repo.get("description", ""),
                    "language": repo.get("language", ""),
                    "stars": repo.get("stargazers_count", 0),
                    "url": repo["html_url"],
                }
                for repo in r.json()
            ]
            return self._ok(f"{len(repos)} repositorios encontrados.", repos=repos)
        except Exception as e:
            return self._err(f"Error: {e}")

    def create_repo(self, name: str, description: str = "", private: bool = False) -> dict:
        """Create a new GitHub repository."""
        if not self._cfg("token"):
            return self._warn("GitHub no configurado.")
        try:
            import requests
            payload = {"name": name, "description": description, "private": private, "auto_init": True}
            r = requests.post(
                f"{self.API_BASE}/user/repos",
                headers=self._headers(),
                json=payload,
                timeout=15,
            )
            r.raise_for_status()
            repo = r.json()
            return self._ok(
                f"Repo creado: {repo['full_name']}",
                url=repo["html_url"],
                clone_url=repo["clone_url"],
                instructions_for_llm=f"Repositorio creado exitosamente: {repo['html_url']}",
            )
        except Exception as e:
            return self._err(f"Error creando repo: {e}")

    def create_issue(self, repo: str, title: str, body: str = "") -> dict:
        """Create an issue on a repo. repo format: 'owner/repo'"""
        if not self._cfg("token"):
            return self._warn("GitHub no configurado.")
        try:
            import requests
            payload = {"title": title, "body": body}
            r = requests.post(
                f"{self.API_BASE}/repos/{repo}/issues",
                headers=self._headers(),
                json=payload,
                timeout=15,
            )
            r.raise_for_status()
            issue = r.json()
            return self._ok(
                f"Issue #{issue['number']} creado en {repo}",
                issue_url=issue["html_url"],
                issue_number=issue["number"],
            )
        except Exception as e:
            return self._err(f"Error: {e}")

    def push_file(self, repo: str, path: str, content: str, message: str = "Actualización de Nova") -> dict:
        """Push/update a file to a GitHub repo."""
        if not self._cfg("token"):
            return self._warn("GitHub no configurado.")
        try:
            import requests
            import base64

            # Check if file exists (to get SHA for update)
            existing = requests.get(
                f"{self.API_BASE}/repos/{repo}/contents/{path}",
                headers=self._headers(),
                timeout=10,
            )
            sha = existing.json().get("sha") if existing.status_code == 200 else None

            payload = {
                "message": message,
                "content": base64.b64encode(content.encode()).decode(),
            }
            if sha:
                payload["sha"] = sha

            r = requests.put(
                f"{self.API_BASE}/repos/{repo}/contents/{path}",
                headers=self._headers(),
                json=payload,
                timeout=15,
            )
            r.raise_for_status()
            return self._ok(f"Archivo '{path}' subido a {repo}.", path=path)
        except Exception as e:
            return self._err(f"Error: {e}")

    # ── Unified Contract ────────────────────────────────────────────
    def _execute(self, request: str) -> dict:
        req = request.strip().lower()
        if "repo" in req and ("crear" in req or "create" in req or "nuevo" in req):
            name = request.strip().split()[-1]
            return self.create_repo(name)
        if "listar" in req or "repos" in req:
            return self.list_repos()
        if "issue" in req:
            parts = request.strip().split(None, 2)
            if len(parts) >= 3:
                return self.create_issue(parts[1], parts[2])
        if "usuario" in req or "user" in req or "perfil" in req:
            return self.get_user()
        return self.get_user()
