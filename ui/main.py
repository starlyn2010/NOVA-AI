import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
import sys
import os
import re
import json
import random
import tempfile
import wave
import datetime

# Add parent directory to path to import core
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from orchestrator import Orchestrator

try:
    from tkinterweb import HtmlFrame
    HAS_TKINTERWEB = True
except ImportError:
    HAS_TKINTERWEB = False

# ─────────────────────────────────────────────────────────────────
#  Nova UI v2.8.0 — Production Interface
# ─────────────────────────────────────────────────────────────────

class NovaUI:
    VERSION = "2.8.0"

    def __init__(self, root):
        self.root = root
        self.root.title(f"Nova v{self.VERSION} — AI Assistant")
        self.root.geometry("1200x780")
        self.root.minsize(900, 600)

        # ── Theme ──────────────────────────────────────────────────
        self.colors = {
            "bg":           "#0f0f0f",
            "bg_secondary": "#1a1a2e",
            "bg_tertiary":  "#16213e",
            "surface":      "#1e1e2e",
            "surface_alt":  "#252540",
            "fg":           "#e0e0e0",
            "fg_dim":       "#8888aa",
            "accent":       "#38bdf8",
            "accent_glow":  "#0ea5e9",
            "success":      "#10b981",
            "warning":      "#fbbf24",
            "error":        "#ef4444",
            "border":       "#2a2a4a",
            "user_bubble":  "#1e3a5f",
            "nova_bubble":  "#1e1e2e",
        }

        self.root.configure(bg=self.colors["bg"])

        # ── Styles ─────────────────────────────────────────────────
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TFrame", background=self.colors["bg"])
        style.configure("TLabel", background=self.colors["bg"], foreground=self.colors["fg"])
        style.configure("TButton", background=self.colors["accent"], foreground="black", borderwidth=0)
        style.configure("TNotebook", background=self.colors["surface"], borderwidth=0)
        style.configure("TNotebook.Tab", background=self.colors["surface"], foreground=self.colors["fg"], padding=[12, 6])
        style.map("TNotebook.Tab", background=[("selected", self.colors["accent"])], foreground=[("selected", "black")])

        # ── State ──────────────────────────────────────────────────
        self.orchestrator = None
        self.current_code = ""
        self.is_recording = False
        self._mic_stream = None
        self._audio_frames = []

        # ── Layout ─────────────────────────────────────────────────
        self._build_header()
        self._build_main_area()
        self._build_status_bar()

        # ── Init ───────────────────────────────────────────────────
        threading.Thread(target=self._init_nova, daemon=True).start()

    # ═══════════════════════════════════════════════════════════════
    #  HEADER BAR
    # ═══════════════════════════════════════════════════════════════
    def _build_header(self):
        header = tk.Frame(self.root, bg=self.colors["bg_secondary"], height=48)
        header.pack(fill=tk.X)
        header.pack_propagate(False)

        # Logo
        tk.Label(
            header, text="🛰️ Nova", font=("Segoe UI", 14, "bold"),
            bg=self.colors["bg_secondary"], fg=self.colors["accent"],
        ).pack(side=tk.LEFT, padx=15)

        # Version badge
        badge = tk.Label(
            header, text=f"v{self.VERSION}", font=("Segoe UI", 8),
            bg=self.colors["accent"], fg="black", padx=6, pady=1,
        )
        badge.pack(side=tk.LEFT, pady=12)

        # Right side: new chat + connector status
        tk.Button(
            header, text="🗑️ Limpiar Chat", command=self._clear_chat,
            bg=self.colors["surface_alt"], fg=self.colors["fg_dim"],
            relief=tk.FLAT, font=("Segoe UI", 8), padx=8,
        ).pack(side=tk.RIGHT, padx=5, pady=10)

        tk.Button(
            header, text="🔌 Conectores", command=self._show_connectors,
            bg=self.colors["surface_alt"], fg=self.colors["fg_dim"],
            relief=tk.FLAT, font=("Segoe UI", 8), padx=8,
        ).pack(side=tk.RIGHT, padx=5, pady=10)

    # ═══════════════════════════════════════════════════════════════
    #  MAIN AREA (Chat + Artifacts)
    # ═══════════════════════════════════════════════════════════════
    def _build_main_area(self):
        self.paned = tk.PanedWindow(
            self.root, orient=tk.HORIZONTAL, bg=self.colors["border"],
            sashwidth=3, borderwidth=0,
        )
        self.paned.pack(fill=tk.BOTH, expand=True)

        # ─── LEFT: Chat Panel ──────────────────────────────────────
        left = tk.Frame(self.paned, bg=self.colors["bg"])
        self.paned.add(left, width=500)

        # Chat display
        self.chat_area = scrolledtext.ScrolledText(
            left, wrap=tk.WORD, bg=self.colors["bg"], fg=self.colors["fg"],
            font=("Segoe UI", 10), insertbackground="white",
            state="disabled", borderwidth=0, padx=12, pady=8,
            selectbackground=self.colors["accent"], spacing3=4,
        )
        self.chat_area.pack(fill=tk.BOTH, expand=True, padx=8, pady=(8, 0))

        # Chat tags
        self.chat_area.tag_config("user_name", foreground=self.colors["accent"], font=("Segoe UI", 10, "bold"))
        self.chat_area.tag_config("nova_name", foreground=self.colors["success"], font=("Segoe UI", 10, "bold"))
        self.chat_area.tag_config("user_text", foreground="#b8d4e3")
        self.chat_area.tag_config("nova_text", foreground=self.colors["fg"])
        self.chat_area.tag_config("system", foreground=self.colors["fg_dim"], font=("Segoe UI", 9, "italic"))
        self.chat_area.tag_config("timestamp", foreground="#555577", font=("Segoe UI", 7))

        # Input frame
        input_frame = tk.Frame(left, bg=self.colors["bg_secondary"], padx=8, pady=8)
        input_frame.pack(fill=tk.X, padx=8, pady=8)

        # Mic button
        self.mic_btn = tk.Button(
            input_frame, text="🎙️", command=self._toggle_mic,
            bg=self.colors["surface_alt"], fg="white",
            relief=tk.FLAT, font=("Segoe UI", 14), width=3,
            activebackground=self.colors["error"],
        )
        self.mic_btn.pack(side=tk.LEFT, padx=(0, 6))

        # Text input
        self.input_field = tk.Text(
            input_frame, height=3, bg=self.colors["surface"], fg=self.colors["fg"],
            font=("Segoe UI", 10), insertbackground="white",
            relief=tk.FLAT, padx=10, pady=8, wrap=tk.WORD,
            selectbackground=self.colors["accent"],
        )
        self.input_field.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.input_field.bind("<Return>", self._on_enter)
        self.input_field.insert("1.0", "Escribe tu mensaje...")
        self.input_field.config(fg=self.colors["fg_dim"])
        self.input_field.bind("<FocusIn>", self._clear_placeholder)
        self.input_field.bind("<FocusOut>", self._add_placeholder)

        # Send button
        self.send_btn = tk.Button(
            input_frame, text="➤", command=self._send_message,
            bg=self.colors["accent"], fg="black",
            relief=tk.FLAT, font=("Segoe UI", 14, "bold"), width=3,
            activebackground=self.colors["accent_glow"],
        )
        self.send_btn.pack(side=tk.RIGHT, padx=(6, 0))

        # ─── RIGHT: Artifact Panel ────────────────────────────────
        right = tk.Frame(self.paned, bg=self.colors["surface"])
        self.paned.add(right, width=700)

        # Artifact header
        art_header = tk.Frame(right, bg=self.colors["surface_alt"], height=40)
        art_header.pack(fill=tk.X)
        art_header.pack_propagate(False)

        self.art_title_label = tk.Label(
            art_header, text="Sin Artifact seleccionado",
            bg=self.colors["surface_alt"], fg=self.colors["accent"],
            font=("Segoe UI", 9, "bold"),
        )
        self.art_title_label.pack(side=tk.LEFT, padx=15, pady=8)

        tk.Button(
            art_header, text="📋 Copiar", command=self._copy_to_clipboard,
            bg=self.colors["surface"], fg="white", relief=tk.FLAT, font=("Segoe UI", 8),
        ).pack(side=tk.RIGHT, padx=5)

        tk.Button(
            art_header, text="💾 Guardar", command=self._save_artifact,
            bg=self.colors["surface"], fg="white", relief=tk.FLAT, font=("Segoe UI", 8),
        ).pack(side=tk.RIGHT, padx=5)

        # Tabs
        self.art_tabs = ttk.Notebook(right)
        self.art_tabs.pack(fill=tk.BOTH, expand=True)

        # Tab 1: Code
        self.code_view = scrolledtext.ScrolledText(
            self.art_tabs, bg="#1e1e2e", fg="#d4d4d4",
            font=("Cascadia Code", 11), borderwidth=0, padx=12, pady=8,
            insertbackground="white",
        )
        self.art_tabs.add(self.code_view, text=" 📝 Código ")

        # Tab 2: Preview
        if HAS_TKINTERWEB:
            self.preview_frame = HtmlFrame(self.art_tabs, messages_enabled=False)
            self.art_tabs.add(self.preview_frame, text=" 🌐 Vista Previa ")
        else:
            self.preview_frame = scrolledtext.ScrolledText(
                self.art_tabs, bg="#333", fg="#888", font=("Segoe UI", 10),
            )
            self.preview_frame.insert("1.0", "Vista previa no disponible.\nInstala 'tkinterweb' para ver HTML.")
            self.preview_frame.configure(state="disabled")
            self.art_tabs.add(self.preview_frame, text=" 🌐 Preview (Off) ")

    # ═══════════════════════════════════════════════════════════════
    #  STATUS BAR
    # ═══════════════════════════════════════════════════════════════
    def _build_status_bar(self):
        bar = tk.Frame(self.root, bg=self.colors["bg_secondary"], height=24)
        bar.pack(fill=tk.X, side=tk.BOTTOM)
        bar.pack_propagate(False)

        self.status_label = tk.Label(
            bar, text="Iniciando Nova...", bg=self.colors["bg_secondary"],
            fg=self.colors["fg_dim"], font=("Segoe UI", 8),
        )
        self.status_label.pack(side=tk.LEFT, padx=10)

        self.engine_label = tk.Label(
            bar, text="", bg=self.colors["bg_secondary"],
            fg=self.colors["fg_dim"], font=("Segoe UI", 8),
        )
        self.engine_label.pack(side=tk.RIGHT, padx=10)

    # ═══════════════════════════════════════════════════════════════
    #  INITIALIZATION
    # ═══════════════════════════════════════════════════════════════
    def _init_nova(self):
        try:
            self.orchestrator = Orchestrator()
            self._update_status(f"Nova v{self.VERSION} Ready — Ollama Connected")
            self._append_system("Nova conectada y lista. Escribe tu mensaje o usa 🎙️ para hablar.")
            # Don't load old history on fresh start
        except Exception as e:
            self._update_status("Error fatal")
            self._append_system(f"Error: {e}")

    # ═══════════════════════════════════════════════════════════════
    #  MICROPHONE (LIVE AUDIO INPUT)
    # ═══════════════════════════════════════════════════════════════
    def _toggle_mic(self):
        if self.is_recording:
            self._stop_recording()
        else:
            self._start_recording()

    def _start_recording(self):
        try:
            import pyaudio
        except ImportError:
            self._append_system("PyAudio no instalado. Ejecuta: pip install pyaudio")
            return

        self.is_recording = True
        self.mic_btn.config(bg=self.colors["error"], text="⏹️")
        self._update_status("🎙️ Grabando... (haz clic para detener)")
        self._audio_frames = []

        def record():
            try:
                pa = pyaudio.PyAudio()
                stream = pa.open(
                    format=pyaudio.paInt16,
                    channels=1,
                    rate=16000,
                    input=True,
                    frames_per_buffer=1024,
                )
                self._mic_stream = stream

                while self.is_recording:
                    data = stream.read(1024, exception_on_overflow=False)
                    self._audio_frames.append(data)

                stream.stop_stream()
                stream.close()
                pa.terminate()
            except Exception as e:
                self.root.after(0, lambda: self._append_system(f"Error microfóno: {e}"))
                self.is_recording = False

        threading.Thread(target=record, daemon=True).start()

    def _stop_recording(self):
        self.is_recording = False
        self.mic_btn.config(bg=self.colors["surface_alt"], text="🎙️")
        self._update_status("Procesando audio...")

        if not self._audio_frames:
            self._update_status("Sin audio grabado.")
            return

        def transcribe():
            try:
                # Save to temp WAV file
                tmp = os.path.join(tempfile.gettempdir(), "nova_recording.wav")
                with wave.open(tmp, "wb") as wf:
                    wf.setnchannels(1)
                    wf.setsampwidth(2)
                    wf.setframerate(16000)
                    wf.writeframes(b"".join(self._audio_frames))

                # Use the audio engine for STT
                if self.orchestrator:
                    result = self.orchestrator.process_request(f"transcribir {tmp}")
                    transcription = result.get("transcription", "") or result.get("text", "")
                    
                    if transcription and not transcription.startswith("Error"):
                        self.root.after(0, lambda: self.input_field.delete("1.0", tk.END))
                        self.root.after(0, lambda: self.input_field.insert("1.0", transcription))
                        self._update_status("Enviando comando de voz...")
                        # Auto-send with is_voice=True
                        threading.Thread(target=self._process_request, args=(transcription, True), daemon=True).start()
                    else:
                        self._update_status("No se pudo transcribir el audio.")
                else:
                    self._update_status("Orchestrator no disponible.")

                # Clean up
                if os.path.exists(tmp):
                    os.remove(tmp)
            except Exception as e:
                self.root.after(0, lambda: self._append_system(f"Error transcripción: {e}"))

        threading.Thread(target=transcribe, daemon=True).start()

    # ═══════════════════════════════════════════════════════════════
    #  CHAT LOGIC
    # ═══════════════════════════════════════════════════════════════
    def _clear_placeholder(self, event=None):
        if self.input_field.get("1.0", "end-1c") == "Escribe tu mensaje...":
            self.input_field.delete("1.0", tk.END)
            self.input_field.config(fg=self.colors["fg"])

    def _add_placeholder(self, event=None):
        if not self.input_field.get("1.0", "end-1c").strip():
            self.input_field.insert("1.0", "Escribe tu mensaje...")
            self.input_field.config(fg=self.colors["fg_dim"])

    def _on_enter(self, event):
        if not (event.state & 0x0001):  # Shift not held
            self._send_message()
            return "break"

    def _send_message(self):
        if not self.orchestrator:
            return
        text = self.input_field.get("1.0", "end-1c").strip()
        if not text or text == "Escribe tu mensaje...":
            return

        self.input_field.delete("1.0", tk.END)
        self._append_user_message(text)
        self._update_status("Generando respuesta...")
        self.send_btn.config(state=tk.DISABLED)
        threading.Thread(target=self._process_request, args=(text,), daemon=True).start()

    def _process_request(self, text, is_voice=False):
        try:
            # Add a timer to update status if it takes long
            def slow_notice():
                import time
                time.sleep(15)
                if self.orchestrator and self.status_label.cget("text") == "Generando respuesta...":
                    self._update_status("🛰️ Nova está procesando con carga alta, un momento...")
            
            threading.Thread(target=slow_notice, daemon=True).start()
            
            response = self.orchestrator.process_request(text, is_voice=is_voice)
            self._save_to_history("user", text)
            self._save_to_history("nova", response.get("text", "") if isinstance(response, dict) else str(response))

            self.root.after(0, lambda: self._append_nova_message(response))

            engine = ""
            if isinstance(response, dict):
                engine = response.get("engine", "")
            self._update_status("Listo")
            if engine:
                self.root.after(0, lambda: self.engine_label.config(text=f"Engine: {engine}"))
        except Exception as e:
            self.root.after(0, lambda: self._append_system(f"Error: {e}"))
        finally:
            self.root.after(0, lambda: self.send_btn.config(state=tk.NORMAL))

    # ═══════════════════════════════════════════════════════════════
    #  MESSAGE RENDERING
    # ═══════════════════════════════════════════════════════════════
    def _append_user_message(self, text):
        self.chat_area.configure(state="normal")
        ts = datetime.datetime.now().strftime("%H:%M")
        self.chat_area.insert(tk.END, f"\n  {ts}  ", "timestamp")
        self.chat_area.insert(tk.END, "Tú\n", "user_name")
        self.chat_area.insert(tk.END, f"  {text}\n", "user_text")
        self.chat_area.see(tk.END)
        self.chat_area.configure(state="disabled")

    def _append_nova_message(self, content):
        self.chat_area.configure(state="normal")

        text = content
        action_req = None
        if isinstance(content, dict):
            text = content.get("text", "")
            action_req = content.get("action_request")

        # Detect & extract artifacts
        artifacts = re.findall(
            r'<artifact title="(.*?)" type="(.*?)">(.*?)</artifact>',
            text, re.DOTALL,
        )
        display_text = re.sub(
            r'<artifact.*?>.*?</artifact>', '', text, flags=re.DOTALL,
        ).strip()

        ts = datetime.datetime.now().strftime("%H:%M")
        self.chat_area.insert(tk.END, f"\n  {ts}  ", "timestamp")
        self.chat_area.insert(tk.END, "Nova\n", "nova_name")

        if display_text:
            self.chat_area.insert(tk.END, f"  {display_text}\n", "nova_text")

        # Create artifact cards
        for title, atype, code in artifacts:
            self._create_artifact_card(title, atype, code)

        # Action card
        if action_req:
            self._create_action_card(action_req)

        self.chat_area.see(tk.END)
        self.chat_area.configure(state="disabled")

    def _append_system(self, text):
        self.chat_area.configure(state="normal")
        self.chat_area.insert(tk.END, f"\n  ▸ {text}\n", "system")
        self.chat_area.see(tk.END)
        self.chat_area.configure(state="disabled")

    # ═══════════════════════════════════════════════════════════════
    #  ARTIFACT CARDS
    # ═══════════════════════════════════════════════════════════════
    def _create_artifact_card(self, title, atype, code):
        card = tk.Frame(
            self.chat_area, bg=self.colors["surface_alt"],
            bd=0, padx=12, pady=6,
        )

        icon = "🌐" if atype in ["html", "web"] else "📄"
        tk.Label(
            card, text=f"{icon} {title}", bg=self.colors["surface_alt"],
            fg=self.colors["accent"], font=("Segoe UI", 9, "bold"),
        ).pack(side=tk.LEFT)

        tk.Label(
            card, text=f" [{atype.upper()}]", bg=self.colors["surface_alt"],
            fg=self.colors["fg_dim"], font=("Segoe UI", 8),
        ).pack(side=tk.LEFT)

        tk.Button(
            card, text="⬅ Ver Artifact",
            command=lambda: self._update_artifact(code, title, atype),
            bg=self.colors["accent"], fg="black", relief=tk.FLAT,
            font=("Segoe UI", 8), padx=10,
        ).pack(side=tk.RIGHT, padx=5)

        self.chat_area.window_create(tk.END, window=card)
        self.chat_area.insert(tk.END, "\n")

    def _update_artifact(self, content, title, atype):
        self.current_code = content.strip()
        self.art_title_label.config(text=f"ARTIFACT: {title} ({atype.upper()})")

        self.code_view.delete("1.0", tk.END)
        self.code_view.insert(tk.END, self.current_code)

        if atype.lower() in ["html", "web"]:
            if HAS_TKINTERWEB:
                self.preview_frame.load_html(self.current_code)
                self.art_tabs.select(1)
            else:
                self.art_tabs.select(0)
        else:
            self.art_tabs.select(0)

    def _create_action_card(self, action):
        card = tk.Frame(
            self.chat_area, bg=self.colors["bg_tertiary"],
            bd=0, padx=12, pady=8,
        )

        tk.Label(
            card, text=f"⚡ {action.get('name', 'Acción')}",
            bg=self.colors["bg_tertiary"], fg=self.colors["warning"],
            font=("Segoe UI", 9, "bold"),
        ).pack(anchor=tk.W)

        tk.Label(
            card, text=action.get("description", ""),
            bg=self.colors["bg_tertiary"], fg=self.colors["fg_dim"],
            font=("Segoe UI", 8),
        ).pack(anchor=tk.W, pady=(2, 5))

        tk.Button(
            card, text="✅ Ejecutar",
            command=lambda: self._run_action(action),
            bg=self.colors["success"], fg="white", relief=tk.FLAT,
            font=("Segoe UI", 8, "bold"), padx=15,
        ).pack(side=tk.LEFT, pady=5)

        self.chat_area.window_create(tk.END, window=card)
        self.chat_area.insert(tk.END, "\n")

    def _run_action(self, action):
        self._append_system(f"Ejecutando: {action.get('name', '')}...")

        def task():
            try:
                res = self.orchestrator.execute_script(action["script"])
                if "error" in res:
                    self.root.after(0, lambda: self._append_system(f"❌ {res['error']}"))
                else:
                    self.root.after(0, lambda: self._append_system(f"✅ {res.get('output', 'OK')}"))
            except Exception as e:
                self.root.after(0, lambda: self._append_system(f"❌ {e}"))

        threading.Thread(target=task, daemon=True).start()

    # ═══════════════════════════════════════════════════════════════
    #  CONNECTOR STATUS PANEL
    # ═══════════════════════════════════════════════════════════════
    def _show_connectors(self):
        win = tk.Toplevel(self.root)
        win.title("🔌 Estado de Conectores — Nova v2.8.0")
        win.geometry("500x600")
        win.configure(bg=self.colors["bg"])

        tk.Label(
            win, text="Conectores de Nova", bg=self.colors["bg"],
            fg=self.colors["accent"], font=("Segoe UI", 14, "bold"),
        ).pack(pady=15)

        connectors = [
            ("🤖 Telegram", "telegram", "telegram_connector", "TelegramConnector"),
            ("📱 WhatsApp", "whatsapp", "whatsapp_connector", "WhatsAppConnector"),
            ("💻 VS Code", "vscode", "vscode_connector", "VSCodeConnector"),
            ("🖼️ Pixazo AI", "pixazo", "pixazo_connector", "PixazoConnector"),
            ("🎨 Canva", "canva", "canva_connector", "CanvaConnector"),
            ("📺 YouTube", "youtube", "youtube_connector", "YouTubeConnector"),
            ("🐙 GitHub", "github", "github_connector", "GitHubConnector"),
            ("📅 Google", "google", "google_connector", "GoogleConnector"),
            ("📝 Notion", "notion", "notion_connector", "NotionConnector"),
            ("🎵 Spotify", "spotify", "spotify_connector", "SpotifyConnector"),
            ("🔢 Wolfram", "wolfram", "services_connector", "WolframConnector"),
            ("📋 Trello", "trello", "services_connector", "TrelloConnector"),
            ("🚀 Vercel", "vercel", "services_connector", "VercelConnector"),
        ]

        canvas = tk.Canvas(win, bg=self.colors["bg"], highlightthickness=0)
        scrollbar = ttk.Scrollbar(win, orient=tk.VERTICAL, command=canvas.yview)
        scroll_frame = tk.Frame(canvas, bg=self.colors["bg"])

        scroll_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=15)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        for label, name, module, cls_name in connectors:
            row = tk.Frame(scroll_frame, bg=self.colors["surface"], pady=8, padx=12)
            row.pack(fill=tk.X, pady=3)

            # Try to import and health check
            status_text = "?"
            status_color = self.colors["fg_dim"]
            try:
                mod = __import__(f"connectors.{module}", fromlist=[cls_name])
                connector_cls = getattr(mod, cls_name)
                connector = connector_cls()
                hc = connector.health_check()
                if hc.get("status") == "success":
                    status_text = "✅"
                    status_color = self.colors["success"]
                elif hc.get("status") == "warning":
                    status_text = "⚠️"
                    status_color = self.colors["warning"]
                else:
                    status_text = "❌"
                    status_color = self.colors["error"]
            except Exception:
                status_text = "📦"
                status_color = self.colors["fg_dim"]

            tk.Label(
                row, text=f"{label}", bg=self.colors["surface"],
                fg=self.colors["fg"], font=("Segoe UI", 10),
            ).pack(side=tk.LEFT)

            tk.Label(
                row, text=status_text, bg=self.colors["surface"],
                fg=status_color, font=("Segoe UI", 12),
            ).pack(side=tk.RIGHT)

    # ═══════════════════════════════════════════════════════════════
    #  UTILITIES
    # ═══════════════════════════════════════════════════════════════
    def _update_status(self, text):
        self.root.after(0, lambda: self.status_label.config(text=text))

    def _clear_chat(self):
        self.chat_area.configure(state="normal")
        self.chat_area.delete("1.0", tk.END)
        self.chat_area.configure(state="disabled")
        self._append_system("Chat limpiado. ¡Listo para una nueva conversación!")

        # Also clear history file
        history_file = os.path.join(parent_dir, "data", "chat_history.json")
        try:
            with open(history_file, "w", encoding="utf-8") as f:
                json.dump([], f)
        except Exception:
            pass

    def _copy_to_clipboard(self):
        if self.current_code:
            self.root.clipboard_clear()
            self.root.clipboard_append(self.current_code)
            self._update_status("📋 Código copiado al portapapeles.")

    def _save_artifact(self):
        if not self.current_code:
            return
        save_dir = os.path.join(parent_dir, "data", "saved_artifacts")
        os.makedirs(save_dir, exist_ok=True)
        ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filepath = os.path.join(save_dir, f"artifact_{ts}.txt")
        try:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(self.current_code)
            self._update_status(f"💾 Artifact guardado: {filepath}")
        except Exception as e:
            self._update_status(f"Error guardando: {e}")

    def _save_to_history(self, role, text):
        history_file = os.path.join(parent_dir, "data", "chat_history.json")
        try:
            history = []
            if os.path.exists(history_file):
                with open(history_file, "r", encoding="utf-8") as f:
                    history = json.load(f)
            history.append({"role": role, "text": text, "ts": datetime.datetime.now().isoformat()})
            if len(history) > 100:
                history = history[-100:]
            with open(history_file, "w", encoding="utf-8") as f:
                json.dump(history, f, indent=2, ensure_ascii=False)
        except Exception:
            pass


if __name__ == "__main__":
    root = tk.Tk()
    app = NovaUI(root)
    root.mainloop()
