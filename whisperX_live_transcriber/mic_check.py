import sounddevice as sd
import numpy as np
import scipy.io.wavfile as wav 

samplerate = 16000  # Частота дискретизацииls
duration = 5        # секунд

print("🎙️ Говорите что-нибудь в течение 5 секунд...")
recording = sd.rec(int(samplerate * duration), samplerate=samplerate, channels=1, dtype='float32')
sd.wait()

filename = "test_recording.wav"
wav.write(filename, samplerate, (recording * 32767).astype(np.int16))
print(f"✅ Аудио записано и сохранено в {filename}")
