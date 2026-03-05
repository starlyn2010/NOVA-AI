
import pyaudio
import wave
import os

def diag_mic():
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 16000
    CHUNK = 1024
    RECORD_SECONDS = 3
    WAVE_OUTPUT_FILENAME = "mic_test.wav"

    audio = pyaudio.PyAudio()

    print("--- DIAGNÓSTICO DE MICRÓFONO ---")
    print(f"Buscando dispositivos...")
    
    info = audio.get_default_input_device_info()
    print(f"Dispositivo predeterminado: {info.get('name')}")

    try:
        stream = audio.open(format=FORMAT, channels=CHANNELS,
                        rate=RATE, input=True,
                        frames_per_buffer=CHUNK)
        print(f"Grabando {RECORD_SECONDS} segundos...")
        frames = []

        for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
            data = stream.read(CHUNK)
            frames.append(data)

        print("Grabación finalizada.")

        stream.stop_stream()
        stream.close()
        audio.terminate()

        with wave.open(WAVE_OUTPUT_FILENAME, 'wb') as wf:
            wf.setnchannels(CHANNELS)
            wf.setsampwidth(audio.get_sample_size(FORMAT))
            wf.setframerate(RATE)
            wf.writeframes(b''.join(frames))
        
        print(f"Archivo guardado: {os.path.abspath(WAVE_OUTPUT_FILENAME)}")
        print("Si el archivo tiene tamaño > 0, el hardware está respondiendo.")
        print(f"Tamaño: {os.path.getsize(WAVE_OUTPUT_FILENAME)} bytes")

    except Exception as e:
        print(f"ERROR FATAL: {e}")

if __name__ == "__main__":
    diag_mic()
