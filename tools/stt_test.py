
import os
import sys

# Add parent to path
sys.path.append(os.getcwd())

def test_transcription():
    audio_path = "mic_test.wav"
    if not os.path.exists(audio_path):
        print(f"Error: No existe {audio_path}. Corre audio_diag.py primero.")
        return

    # Inyeccion de FFmpeg (WinGet Path)
    ffmpeg_bin = os.path.join(os.environ.get("LOCALAPPDATA", ""), "Microsoft", "WinGet", "Packages", "Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe", "ffmpeg-8.0.1-full_build", "bin")
    if os.path.exists(ffmpeg_bin):
        os.environ["PATH"] += os.pathsep + ffmpeg_bin
        print(f"Inyectando FFmpeg PATH: {ffmpeg_bin}")

    print("--- TEST DE TRANSCRIPCIÓN (WHISPER) ---")
    try:
        import whisper
        print("Cargando modelo 'tiny'...")
        model = whisper.load_model("tiny")
        print("Transcribiendo...")
        result = model.transcribe(audio_path)
        print("\nRESULTADO:")
        print(f"Texto: {result.get('text', '')}")
        print("-" * 20)
    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    test_transcription()
