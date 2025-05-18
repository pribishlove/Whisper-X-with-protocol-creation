import threading
import queue
import numpy as np
import sounddevice as sd
import tempfile
import os
import scipy.io.wavfile as wav
import whisperx
import torch
import re

# --- Настройки ---
SAMPLERATE = 16000
CHUNK_DURATION = 2  # секунд
STOP_PHRASE = "стоп"
language_code = "ru"
device = "cuda" if torch.cuda.is_available() else "cpu"
model_name = "turbo"
compute_type = "float32"

# --- Инициализация ---
audio_queue = queue.Queue()
stop_event = threading.Event()
full_text = ""
buffer_text = ""

# --- Загрузка модели ---
print("🚀 Загрузка модели WhisperX...")
model = whisperx.load_model(
    whisper_arch=model_name,
    device=device,
    language=language_code,
    compute_type=compute_type
)
print("✅ Модель загружена.")

# --- Извлечение завершённых предложений ---
def extract_sentences(text):
    # Ищем завершённые предложения
    matches = list(re.finditer(r'[^.?!]+[.?!]', text))
    sentences = [match.group().strip() for match in matches]
    
    # Остаток — всё после последнего найденного предложения
    if matches:
        last_index = matches[-1].end()
        remainder = text[last_index:].strip()
    else:
        remainder = text.strip()
    
    return sentences, remainder

# --- Запись аудио чанков ---
def record_audio():
    while not stop_event.is_set():
        chunk = sd.rec(int(SAMPLERATE * CHUNK_DURATION),
                       samplerate=SAMPLERATE, channels=1, dtype='float32')
        sd.wait()
        audio_queue.put(np.squeeze(chunk))

# --- Транскрипция чанков ---
def transcribe_loop():
    global full_text, buffer_text
    while not stop_event.is_set() or not audio_queue.empty():
        try:
            chunk = audio_queue.get(timeout=1)
        except queue.Empty:
            continue

        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmpfile:
            wav.write(tmpfile.name, SAMPLERATE, (chunk * 32767).astype(np.int16))
            tmp_path = tmpfile.name

        audio = whisperx.load_audio(tmp_path)
        result = model.transcribe(audio)
        os.remove(tmp_path)

        segments = result.get("segments", [])
        current_raw_text = " ".join(seg["text"].strip().lower() for seg in segments if seg["text"].strip())

        # Пропуск пустых или неинформативных чанков
        if not current_raw_text or "no active speech" in current_raw_text or "No active speech found in audio" in current_raw_text:
            continue

        print(f"\n🎧 Текущий чанк: {current_raw_text}")

        combined_text = buffer_text + " " + current_raw_text
        sentences, buffer_text = extract_sentences(combined_text)

        for sentence in sentences:
            sentence = sentence.strip()
            if sentence and sentence not in full_text:
                capitalized = sentence[0].upper() + sentence[1:] if sentence else ""
                full_text += capitalized + " "
                print(f"✅ Добавлено: {capitalized}")

        if STOP_PHRASE in current_raw_text:
            print("🛑 Обнаружена фраза остановки.")
            stop_event.set()
            break

    print("\n📋 Полная транскрипция:")
    final_text = full_text.strip()
    if final_text:
        final_text = final_text[0].upper() + final_text[1:]
    print(final_text)

# --- Запуск ---
rec_thread = threading.Thread(target=record_audio)
trans_thread = threading.Thread(target=transcribe_loop)

print("Скажите что-нибудь... (Скажите 'стоп' для завершения)")
rec_thread.start()
trans_thread.start()

rec_thread.join()
trans_thread.join()
print("✅ Завершено.")
