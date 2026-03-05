import pyttsx3
import os
import threading

class AudioEngine:
    """
    Motor de Audio de Nova: Maneja Conversión de Texto a Voz (TTS) 
    y Voz a Texto (STT) usando Whisper.
    """
    def __init__(self, model_size="tiny"):
        self.model_size = model_size
        self.stt_model = None
        
        # Inject FFmpeg path if it exists (for Windows WinGet installs)
        ffmpeg_bin = os.path.join(os.environ.get("LOCALAPPDATA", ""), "Microsoft", "WinGet", "Packages", "Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe", "ffmpeg-8.0.1-full_build", "bin")
        if os.path.exists(ffmpeg_bin) and ffmpeg_bin not in os.environ["PATH"]:
            os.environ["PATH"] += os.pathsep + ffmpeg_bin

        # Initialize TTS
        try:
            self.tts_engine = pyttsx3.init()
            voices = self.tts_engine.getProperty('voices')
            for voice in voices:
                if "spanish" in voice.name.lower() or "es-es" in voice.id.lower():
                    self.tts_engine.setProperty('voice', voice.id)
                    break
        except Exception as e:
            print(f"[Audio] Error inicializando TTS: {e}")
            self.tts_engine = None

    def _load_whisper(self):
        """Lazy load of Whisper model."""
        if self.stt_model is None:
            print(f"[Audio] Cargando modelo Whisper '{self.model_size}' (Lazy Load)...")
            try:
                import whisper
                self.stt_model = whisper.load_model(self.model_size)
            except Exception as e:
                print(f"[Audio] Error cargando Whisper: {e}")
                return False
        return True

    def say(self, text: str):
        """TTS síncrono."""
        if not self.tts_engine:
            return
        try:
            self.tts_engine.say(text)
            self.tts_engine.runAndWait()
        except Exception as e:
            print(f"[Audio] Error en TTS: {e}")

    def listen(self, audio_path: str) -> str:
        """STT con Lazy Load."""
        if not self._load_whisper():
            return "Error: No se pudo cargar Whisper."
            
        if not os.path.exists(audio_path):
            return f"Error: No existe {audio_path}"
            
        try:
            result = self.stt_model.transcribe(audio_path)
            return result.get("text", "").strip()
        except Exception as e:
            err_msg = str(e)
            if "WinError 2" in err_msg or "ffmpeg" in err_msg.lower():
                return "Error: ffmpeg no instalado. Es necesario para la transcripción de voz."
            return f"Error en transcripción: {err_msg}"

    def process(self, input_data: str, health_check: bool = False) -> dict:
        """Contrato unificado para el Orchestrator."""
        if health_check:
            # Check if whisper is at least importable (lazy load check)
            try:
                import whisper
                stt_ready = True
            except ImportError:
                stt_ready = False
            return {"status": "success" if stt_ready else "warning", "message": "AudioEngine ready (Whisper missing)."}
            
        # Si el input es una ruta de archivo, transcribimos.
        # De lo contrario, informamos.
        if os.path.exists(input_data) and input_data.lower().endswith(('.wav', '.mp3', '.m4a')):
            text = self.listen(input_data)
            return {
                "status": "success" if not text.startswith("Error") else "error",
                "transcription": text
            }
        return {
            "status": "success",
            "message": "Motor de audio activo. Esperando archivo de voz.",
            "transcription": ""
        }
