"""
Nova Google Services Connector — Production v2.8.0
=====================================================
Google Calendar + Google Drive integration via Google APIs.
"""

import os
import json
import datetime
from .base import BaseConnector


class GoogleConnector(BaseConnector):
    NAME = "google"
    REQUIRED_KEYS = ["credentials_path"]

    def __init__(self):
        super().__init__()
        self._root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self._token_path = os.path.join(self._root, "data", "google_token.json")
        self._creds = None

    def _get_credentials(self):
        """Load or refresh Google OAuth2 credentials."""
        if self._creds:
            return self._creds

        creds_path = self._cfg("credentials_path")
        if not creds_path:
            return None

        if not os.path.isabs(creds_path):
            creds_path = os.path.join(self._root, creds_path)

        try:
            from google.oauth2.credentials import Credentials
            from google_auth_oauthlib.flow import InstalledAppFlow
            from google.auth.transport.requests import Request

            SCOPES = [
                "https://www.googleapis.com/auth/calendar",
                "https://www.googleapis.com/auth/drive",
            ]

            creds = None
            if os.path.exists(self._token_path):
                creds = Credentials.from_authorized_user_file(self._token_path, SCOPES)

            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                else:
                    flow = InstalledAppFlow.from_client_secrets_file(creds_path, SCOPES)
                    creds = flow.run_local_server(port=0)

                with open(self._token_path, "w") as f:
                    f.write(creds.to_json())

            self._creds = creds
            return creds
        except ImportError:
            return None
        except Exception:
            return None

    # ──── CALENDAR ─────────────────────────────────────────────────
    def list_events(self, max_results: int = 10) -> dict:
        """List upcoming calendar events."""
        creds = self._get_credentials()
        if not creds:
            return self._warn(
                "Google no configurado. Necesitas credentials.json de Google Cloud Console.",
                instructions_for_llm=(
                    "Para activar Google Calendar, el usuario debe: "
                    "1) Crear un proyecto en console.cloud.google.com, "
                    "2) Habilitar Google Calendar API, "
                    "3) Descargar credentials.json y poner la ruta en config.yaml → connectors → google → credentials_path"
                ),
            )

        try:
            from googleapiclient.discovery import build

            service = build("calendar", "v3", credentials=creds)
            now = datetime.datetime.utcnow().isoformat() + "Z"
            result = service.events().list(
                calendarId="primary",
                timeMin=now,
                maxResults=max_results,
                singleEvents=True,
                orderBy="startTime",
            ).execute()

            events = [
                {
                    "summary": e.get("summary", "Sin título"),
                    "start": e["start"].get("dateTime", e["start"].get("date")),
                    "end": e["end"].get("dateTime", e["end"].get("date")),
                    "location": e.get("location", ""),
                }
                for e in result.get("items", [])
            ]
            return self._ok(f"{len(events)} eventos próximos.", events=events)
        except Exception as e:
            return self._err(f"Error Calendar: {e}")

    def create_event(self, summary: str, start: str, end: str, description: str = "") -> dict:
        """Create a calendar event. start/end format: '2025-02-20T15:00:00'"""
        creds = self._get_credentials()
        if not creds:
            return self._warn("Google no configurado.")

        try:
            from googleapiclient.discovery import build

            service = build("calendar", "v3", credentials=creds)
            event = {
                "summary": summary,
                "description": description,
                "start": {"dateTime": start, "timeZone": "Europe/Madrid"},
                "end": {"dateTime": end, "timeZone": "Europe/Madrid"},
            }
            result = service.events().insert(calendarId="primary", body=event).execute()
            return self._ok(
                f"Evento creado: {summary}",
                event_id=result.get("id"),
                link=result.get("htmlLink"),
                instructions_for_llm=f"Evento '{summary}' creado. Link: {result.get('htmlLink')}",
            )
        except Exception as e:
            return self._err(f"Error: {e}")

    # ──── DRIVE ────────────────────────────────────────────────────
    def list_files(self, query: str = "", max_results: int = 10) -> dict:
        """List files in Google Drive."""
        creds = self._get_credentials()
        if not creds:
            return self._warn("Google no configurado.")

        try:
            from googleapiclient.discovery import build

            service = build("drive", "v3", credentials=creds)
            q = f"name contains '{query}'" if query else ""
            result = service.files().list(
                q=q, pageSize=max_results,
                fields="files(id, name, mimeType, modifiedTime, size)",
            ).execute()

            files = [
                {
                    "name": f["name"],
                    "id": f["id"],
                    "type": f.get("mimeType", ""),
                    "modified": f.get("modifiedTime", ""),
                    "size": f.get("size", ""),
                }
                for f in result.get("files", [])
            ]
            return self._ok(f"{len(files)} archivos encontrados.", files=files)
        except Exception as e:
            return self._err(f"Error Drive: {e}")

    def upload_file(self, filepath: str, folder_id: str = None) -> dict:
        """Upload a local file to Google Drive."""
        creds = self._get_credentials()
        if not creds:
            return self._warn("Google no configurado.")
        if not os.path.exists(filepath):
            return self._err(f"Archivo no existe: {filepath}")

        try:
            from googleapiclient.discovery import build
            from googleapiclient.http import MediaFileUpload

            service = build("drive", "v3", credentials=creds)
            metadata = {"name": os.path.basename(filepath)}
            if folder_id:
                metadata["parents"] = [folder_id]

            media = MediaFileUpload(filepath, resumable=True)
            result = service.files().create(body=metadata, media_body=media, fields="id,webViewLink").execute()

            return self._ok(
                f"Archivo subido: {os.path.basename(filepath)}",
                file_id=result.get("id"),
                link=result.get("webViewLink"),
            )
        except Exception as e:
            return self._err(f"Error: {e}")

    # ── Unified Contract ────────────────────────────────────────────
    def _execute(self, request: str) -> dict:
        req = request.strip().lower()
        if any(k in req for k in ["evento", "agenda", "reunión", "reunion", "calendar"]):
            if "crear" in req or "agendar" in req:
                return self._warn(
                    "Para crear un evento necesito: título, fecha inicio y fecha fin. "
                    "Ejemplo: crear evento 'Reunión' desde 2025-02-20T15:00:00 hasta 2025-02-20T16:00:00"
                )
            return self.list_events()
        if any(k in req for k in ["archivo", "drive", "subir", "upload"]):
            if "subir" in req or "upload" in req:
                parts = request.strip().split()
                path = parts[-1] if len(parts) > 1 else ""
                return self.upload_file(path)
            return self.list_files(request)
        return self.list_events()
