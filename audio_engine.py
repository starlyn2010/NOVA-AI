"""
Nova v2.8.0 — Audio Engine
Handles Speech-to-Text (STT) and Text-to-Speech (TTS) operations.
Designed for low-resource environments with graceful fallbacks.
"""

import os
import logging
import tempfile

logger = logging.getLogger("AudioEngine")


class AudioEngine:
    """
    Modular audio processing engine for Nova.
    Supports STT via Whisper/Vosk and TTS via pyttsx3/edge-tts.
    All heavy dependencies are imported lazily to keep boot fast.
    """

    def __init__(self):
        self.base_path = os.path.dirname(os.path.abspath(__file__))
        self._stt_engine = None
        self._tts_engine = None

    # ── Speech-to-Text ──────────────────────────────────────────────

    def transcribe(self, audio_path: str) -> dict:
        """
        Transcribes an audio file to text.
        Tries Whisper first, then falls back to Vosk.

        Args:
            audio_path: Path to a WAV/MP3 audio file.

        Returns:
            dict with 'transcription' and 'status' keys.
        """
        if not audio_path or not os.path.exists(audio_path):
            return {"status": "error", "transcription": "", "message": f"Archivo no encontrado: {audio_path}"}

        # Try whisper (OpenAI)
        try:
            return self._transcribe_whisper(audio_path)
        except Exception as e:
            logger.warning(f"Whisper no disponible: {e}")

        # Fallback: Vosk
        try:
            return self._transcribe_vosk(audio_path)
        except Exception as e:
            logger.warning(f"Vosk no disponible: {e}")

        return {
            "status": "error",
            "transcription": "",
            "message": "No hay motor STT disponible. Instala 'openai-whisper' o 'vosk'.",
        }

    def _transcribe_whisper(self, audio_path: str) -> dict:
        import whisper

        if self._stt_engine is None:
            self._stt_engine = whisper.load_model("tiny")
        result = self._stt_engine.transcribe(audio_path, language="es")
        text = result.get("text", "").strip()
        return {"status": "success", "transcription": text}

    def _transcribe_vosk(self, audio_path: str) -> dict:
        import wave
        import json as _json
        from vosk import Model, KaldiRecognizer

        model_path = os.path.join(self.base_path, "models", "vosk-model-small-es")
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Modelo Vosk no encontrado en: {model_path}")

        model = Model(model_path)
        with wave.open(audio_path, "rb") as wf:
            rec = KaldiRecognizer(model, wf.getframerate())
            rec.SetWords(True)
            results = []
            while True:
                data = wf.readframes(4000)
                if len(data) == 0:
                    break
                if rec.AcceptWaveform(data):
                    part = _json.loads(rec.Result())
                    results.append(part.get("text", ""))
            final = _json.loads(rec.FinalResult())
            results.append(final.get("text", ""))

        text = " ".join(r for r in results if r).strip()
        return {"status": "success", "transcription": text}

    # ── Text-to-Speech ──────────────────────────────────────────────

    def speak(self, text: str, output_path: str = None) -> dict:
        """
        Converts text to speech audio.

        Args:
            text: The text to synthesize.
            output_path: Optional path for the output WAV. If None, auto-generates.

        Returns:
            dict with 'status' and 'audio_path' keys.
        """
        if not text:
            return {"status": "error", "audio_path": "", "message": "Texto vacío."}

        if output_path is None:
            output_path = os.path.join(tempfile.gettempdir(), "nova_tts_output.wav")

        try:
            return self._speak_pyttsx3(text, output_path)
        except Exception as e:
            logger.warning(f"pyttsx3 no disponible: {e}")

        return {
            "status": "error",
            "audio_path": "",
            "message": "No hay motor TTS disponible. Instala 'pyttsx3'.",
        }

    def _speak_pyttsx3(self, text: str, output_path: str) -> dict:
        import pyttsx3

        if self._tts_engine is None:
            self._tts_engine = pyttsx3.init()
            self._tts_engine.setProperty("rate", 160)

        self._tts_engine.save_to_file(text, output_path)
        self._tts_engine.runAndWait()
        return {"status": "success", "audio_path": output_path}

    # ── Orchestrator Interface ──────────────────────────────────────

    def process(self, request: str, health_check: bool = False) -> dict:
        """Unified interface for the Orchestrator."""
        if health_check:
            return {"status": "success", "message": "AudioEngine ready."}

        req_lower = (request or "").lower()

        if "transcribir" in req_lower or "transcribe" in req_lower:
            # Extract path from request
            parts = request.split()
            path = parts[-1] if len(parts) > 1 else ""
            return self.transcribe(path)

        return {
            "status": "success",
            "message": "AudioEngine: usa 'transcribir <ruta>' o el micrófono de la UI.",
        }