import os
import numpy as np
import sounddevice as sd
import tempfile
import scipy.io.wavfile as wav
import whisperx
import torch

# Параметры записи 
SAMPLERATE = 16000
CHUNK_DURATION = 5  # секунд
STOP_PHRASE = "закончить аудио"
STOP_PHRASE2 = "Закончить аудио"


# Параметры модели
language_code = "ru" 
min_speakers_count = 1
max_speakers_count = 3
device = "cuda" if torch.cuda.is_available() else "cpu"
whisper_model_name = "turbo" 
compute_type = "float32" 

# Загрузка модели
print("🚀 Загрузка модели WhisperX...")
model = whisperx.load_model(whisper_arch=whisper_model_name, device=device, language=language_code, compute_type=compute_type)
print("✅ Модель загружена.")

def record_and_transcribe():
    print("🎙️ Слушаю... Скажите 'закончить аудио', чтобы завершить.")
    audio_buffer = []

    try:
        while True:
            print(f"⏺️ Запись {CHUNK_DURATION} секунд...")
            chunk = sd.rec(int(SAMPLERATE * CHUNK_DURATION), samplerate=SAMPLERATE, channels=1, dtype='float32')
            sd.wait()
            audio_buffer.append(np.squeeze(chunk))

            # Конкатенация
            audio_data = np.concatenate(audio_buffer)

            # Сохраняем во временный WAV-файл
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmpfile:
                wav.write(tmpfile.name, SAMPLERATE, (audio_data * 32767).astype(np.int16))
                tmp_path = tmpfile.name

            # Загружаем и транскрибируем с whisperx
            print("📄 Транскрибирую...")
            audio = whisperx.load_audio(tmp_path)
            result = model.transcribe(audio)

            # text = result.get("text", "").strip().lower()
            # text = result["segments"] вся инфа 
            text = result["text"]


            print("🗣️ Вы сказали:", text)

            if STOP_PHRASE in text:
                print("🛑 Обнаружена фраза остановки.")
                break

        print("\n📋 Итоговая транскрипция:")
        print(result["text"])

    except Exception as e:
        print("❌ Произошла ошибка:", e)

if __name__ == "__main__":
    record_and_transcribe()
