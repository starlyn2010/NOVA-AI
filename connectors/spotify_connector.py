"""
Nova Spotify Connector — Production v2.8.0
============================================
Control playback, manage playlists via Spotify Web API.
"""

import os
import json
from .base import BaseConnector


class SpotifyConnector(BaseConnector):
    NAME = "spotify"
    REQUIRED_KEYS = ["client_id", "client_secret", "redirect_uri"]
    API_BASE = "https://api.spotify.com/v1"
    AUTH_URL = "https://accounts.spotify.com/api/token"

    def __init__(self):
        super().__init__()
        self._root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self._token_path = os.path.join(self._root, "data", "spotify_token.json")
        self._access_token = None

    def _get_token(self) -> str:
        """Get or refresh Spotify access token."""
        if self._access_token:
            return self._access_token

        # Try saved token
        if os.path.exists(self._token_path):
            try:
                with open(self._token_path, "r") as f:
                    data = json.load(f)
                    self._access_token = data.get("access_token")
                    return self._access_token
            except Exception:
                pass

        # Get new token via client credentials
        client_id = self._cfg("client_id")
        client_secret = self._cfg("client_secret")
        if not client_id or not client_secret:
            return ""

        try:
            import requests
            r = requests.post(
                self.AUTH_URL,
                data={"grant_type": "client_credentials"},
                auth=(client_id, client_secret),
                timeout=10,
            )
            r.raise_for_status()
            data = r.json()
            self._access_token = data["access_token"]

            with open(self._token_path, "w") as f:
                json.dump(data, f)

            return self._access_token
        except Exception:
            return ""

    def _headers(self):
        token = self._get_token()
        return {"Authorization": f"Bearer {token}"}

    def search(self, query: str, search_type: str = "track", limit: int = 5) -> dict:
        """Search Spotify for tracks, artists, albums, or playlists."""
        token = self._get_token()
        if not token:
            return self._warn(
                "Spotify no configurado. Crea una app en https://developer.spotify.com/dashboard",
                instructions_for_llm=(
                    "Para usar Spotify, el usuario debe crear una app en developer.spotify.com "
                    "y poner client_id, client_secret y redirect_uri en config.yaml → connectors → spotify"
                ),
            )
        try:
            import requests
            r = requests.get(
                f"{self.API_BASE}/search",
                headers=self._headers(),
                params={"q": query, "type": search_type, "limit": limit},
                timeout=10,
            )
            r.raise_for_status()
            data = r.json()

            items_key = f"{search_type}s"
            items = data.get(items_key, {}).get("items", [])

            results = []
            for item in items:
                entry = {
                    "name": item.get("name"),
                    "id": item.get("id"),
                    "url": item.get("external_urls", {}).get("spotify", ""),
                }
                if search_type == "track":
                    entry["artist"] = ", ".join(a["name"] for a in item.get("artists", []))
                    entry["album"] = item.get("album", {}).get("name", "")
                    entry["preview_url"] = item.get("preview_url", "")
                elif search_type == "artist":
                    entry["genres"] = item.get("genres", [])
                    entry["popularity"] = item.get("popularity", 0)
                results.append(entry)

            return self._ok(
                f"{len(results)} resultados de {search_type} para '{query}'.",
                results=results,
                instructions_for_llm=f"Encontré {len(results)} {search_type}s para '{query}': "
                + ", ".join(r["name"] for r in results),
            )
        except Exception as e:
            return self._err(f"Error Spotify: {e}")

    def get_recommendations(self, seed_genres: str = "pop,rock", limit: int = 5) -> dict:
        """Get track recommendations based on genres."""
        token = self._get_token()
        if not token:
            return self._warn("Spotify no configurado.")
        try:
            import requests
            r = requests.get(
                f"{self.API_BASE}/recommendations",
                headers=self._headers(),
                params={"seed_genres": seed_genres, "limit": limit},
                timeout=10,
            )
            r.raise_for_status()
            tracks = [
                {
                    "name": t["name"],
                    "artist": ", ".join(a["name"] for a in t.get("artists", [])),
                    "url": t.get("external_urls", {}).get("spotify", ""),
                }
                for t in r.json().get("tracks", [])
            ]
            return self._ok(f"Recomendaciones ({seed_genres}):", tracks=tracks)
        except Exception as e:
            return self._err(f"Error: {e}")

    def _execute(self, request: str) -> dict:
        req = request.strip().lower()
        if "recomendar" in req or "recomienda" in req or "sugerir" in req:
            genre = "pop"
            for g in ["rock", "jazz", "classical", "electronic", "hip-hop", "r-n-b", "latin", "lo-fi"]:
                if g in req:
                    genre = g
                    break
            return self.get_recommendations(seed_genres=genre)
        return self.search(request)
