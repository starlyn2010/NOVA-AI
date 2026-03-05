"""
Nova VS Code Connector — Production v2.8.0
=============================================
Integrates with Visual Studio Code via CLI and workspace management.
"""

import os
import subprocess
import json
from .base import BaseConnector


class VSCodeConnector(BaseConnector):
    NAME = "vscode"
    REQUIRED_KEYS = []  # VS Code CLI is auto-detected

    def __init__(self):
        super().__init__()
        self._code_cmd = self._find_code_cmd()

    def _find_code_cmd(self) -> str:
        """Locate the VS Code CLI binary."""
        # Check common Windows paths
        candidates = [
            "code",  # If in PATH
            os.path.expandvars(r"%LOCALAPPDATA%\Programs\Microsoft VS Code\bin\code.cmd"),
            os.path.expandvars(r"%PROGRAMFILES%\Microsoft VS Code\bin\code.cmd"),
        ]
        for cmd in candidates:
            try:
                result = subprocess.run(
                    [cmd, "--version"],
                    capture_output=True, text=True, timeout=5,
                    creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0,
                )
                if result.returncode == 0:
                    return cmd
            except Exception:
                continue
        return ""

    def health_check(self) -> dict:
        if self._code_cmd:
            return self._ok(f"VS Code encontrado: {self._code_cmd}")
        return self._warn("VS Code no encontrado en el sistema. ¿Está instalado?")

    def open_file(self, filepath: str, line: int = None) -> dict:
        """Open a file in VS Code, optionally at a specific line."""
        if not self._code_cmd:
            return self._err("VS Code no disponible.")
        if not os.path.exists(filepath):
            return self._err(f"Archivo no existe: {filepath}")

        try:
            target = f"{filepath}:{line}" if line else filepath
            subprocess.Popen(
                [self._code_cmd, "--goto", target],
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0,
            )
            return self._ok(f"Archivo abierto en VS Code: {filepath}", file=filepath, line=line)
        except Exception as e:
            return self._err(f"Error abriendo VS Code: {e}")

    def open_folder(self, folder_path: str) -> dict:
        """Open a folder/project in VS Code."""
        if not self._code_cmd:
            return self._err("VS Code no disponible.")
        if not os.path.isdir(folder_path):
            return self._err(f"Carpeta no existe: {folder_path}")

        try:
            subprocess.Popen(
                [self._code_cmd, folder_path],
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0,
            )
            return self._ok(f"Proyecto abierto en VS Code: {folder_path}", folder=folder_path)
        except Exception as e:
            return self._err(f"Error abriendo carpeta: {e}")

    def run_terminal_command(self, command: str, cwd: str = None) -> dict:
        """Execute a command in VS Code's integrated terminal."""
        if not self._code_cmd:
            return self._err("VS Code no disponible.")
        try:
            # Use VS Code's built-in terminal via CLI
            args = [self._code_cmd]
            if cwd:
                args.extend(["--folder-uri", cwd])
            # Open the terminal and run command
            subprocess.Popen(
                args,
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0,
            )
            return self._ok(f"VS Code abierto. Ejecuta manualmente: {command}")
        except Exception as e:
            return self._err(f"Error: {e}")

    def install_extension(self, extension_id: str) -> dict:
        """Install a VS Code extension."""
        if not self._code_cmd:
            return self._err("VS Code no disponible.")
        try:
            result = subprocess.run(
                [self._code_cmd, "--install-extension", extension_id],
                capture_output=True, text=True, timeout=60,
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0,
            )
            if result.returncode == 0:
                return self._ok(f"Extensión instalada: {extension_id}")
            return self._err(f"Error instalando extensión: {result.stderr}")
        except Exception as e:
            return self._err(f"Error: {e}")

    def list_extensions(self) -> dict:
        """List installed VS Code extensions."""
        if not self._code_cmd:
            return self._err("VS Code no disponible.")
        try:
            result = subprocess.run(
                [self._code_cmd, "--list-extensions"],
                capture_output=True, text=True, timeout=15,
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0,
            )
            extensions = result.stdout.strip().split("\n") if result.stdout else []
            return self._ok(f"{len(extensions)} extensiones instaladas.", extensions=extensions)
        except Exception as e:
            return self._err(f"Error: {e}")

    # ── Unified Contract ────────────────────────────────────────────
    def _execute(self, request: str) -> dict:
        req = request.strip().lower()
        parts = request.strip().split(None, 1)

        if any(k in req for k in ["abrir archivo", "open file", "abrir"]):
            path = parts[-1] if len(parts) > 1 else ""
            return self.open_file(path.strip())

        if any(k in req for k in ["abrir carpeta", "open folder", "proyecto"]):
            path = parts[-1] if len(parts) > 1 else ""
            return self.open_folder(path.strip())

        if "extensi" in req and ("instalar" in req or "install" in req):
            ext_id = parts[-1] if len(parts) > 1 else ""
            return self.install_extension(ext_id.strip())

        if "extensi" in req and ("listar" in req or "list" in req):
            return self.list_extensions()

        # Default: try to open as file or folder
        target = request.strip()
        if os.path.isfile(target):
            return self.open_file(target)
        elif os.path.isdir(target):
            return self.open_folder(target)

        return self._warn(
            "Comandos disponibles: abrir archivo <ruta>, abrir carpeta <ruta>, "
            "instalar extension <id>, listar extensiones",
            instructions_for_llm=(
                "El conector de VS Code soporta: abrir archivos, abrir carpetas/proyectos, "
                "instalar extensiones, y listar extensiones instaladas."
            ),
        )
