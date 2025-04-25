import threading
import queue
import numpy as np
import sounddevice as sd
import tempfile
import scipy.io.wavfile as wav
import whisperx
import torch

# --- Настройки ---
SAMPLERATE = 16000
CHUNK_DURATION = 5  # секунд
#STOP_PHRASE = "закончить аудио"
language_code = "ru"
device = "cuda" if torch.cuda.is_available() else "cpu"
model_name = "turbo"
compute_type = "float32"

# --- Очередь аудио чанков ---
audio_queue = queue.Queue()
stop_event = threading.Event()

# --- Загрузка модели ---
print("🚀 Загрузка модели WhisperX...")
model = whisperx.load_model(whisper_arch=model_name, device=device, language=language_code, compute_type=compute_type)
print("✅ Модель загружена.")

# --- Запись чанков ---
def record_audio():
    while not stop_event.is_set():
#        print("🎙️ Запись чанка...")
        chunk = sd.rec(int(SAMPLERATE * CHUNK_DURATION), samplerate=SAMPLERATE, channels=1, dtype='float32')
        sd.wait()
        audio_queue.put(np.squeeze(chunk))
#        print("📦 Чанк добавлен в очередь.")

# --- Транскрипция чанков ---
def transcribe_loop():
    full_transcript = ""
    while not stop_event.is_set() or not audio_queue.empty():
        try:
            chunk = audio_queue.get(timeout=1)
        except queue.Empty:
            continue
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmpfile:
            wav.write(tmpfile.name, SAMPLERATE, (chunk * 32767).astype(np.int16))
            tmp_path = tmpfile.name

#        print("📄 Транскрибирую чанк...")
        audio = whisperx.load_audio(tmp_path)
        result = model.transcribe(audio)
        segments = result.get("segments", [])
        for seg in segments:
            clean_text = seg["text"].strip().lower()  # удаляет лишние пробелы и уберает заглавные буквы
            print(clean_text)
            # full_transcript += " " + text

        # if STOP_PHRASE in text:
        #     print("🛑 Обнаружена фраза остановки.")
        #     stop_event.set()


    # print("\n📋 Полная транскрипция:")
    # print(full_transcript.strip())

# --- Запуск потоков ---
rec_thread = threading.Thread(target=record_audio)
trans_thread = threading.Thread(target=transcribe_loop)

print("▶️ Начинаем...")
rec_thread.start()
trans_thread.start()

rec_thread.join()
trans_thread.join()
print("✅ Завершено.")
