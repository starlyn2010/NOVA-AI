
import sys
import os

# Add root
sys.path.append(os.getcwd())

from engines.audio.audio_engine import AudioEngine

def test_mouth():
    print("--- PROBANDO BOCA DE NOVA (TTS) ---")
    engine = AudioEngine()
    
    test_text = "Hola. Soy Nova. Mi sistema de voz está operativo, pero actualmente está en modo silencioso por eficiencia industrial."
    print(f"Hablando: {test_text}")
    
    engine.say(test_text)
    print("Prueba finalizada.")

if __name__ == "__main__":
    test_mouth()
