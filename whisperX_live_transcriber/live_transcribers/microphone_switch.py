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

# --- Функция выбора аудиоустройства ---
def choose_audio_device():
    print("\n🎛️ Доступные устройства ввода:")
    devices = sd.query_devices()
    input_devices = [(i, d) for i, d in enumerate(devices) if d['max_input_channels'] > 0]

    for i, dev in input_devices:
        print(f"[{i}] {dev['name']} ({dev['hostapi']})")

    while True:
        try:
            idx = int(input("🔘 Выберите устройство ввода (по номеру): "))
            if any(i == idx for i, _ in input_devices):
                return idx
        except ValueError:
            pass
        print("❌ Неверный выбор, попробуйте снова.")

# --- Извлечение завершённых предложений ---
def extract_sentences(text):
    matches = list(re.finditer(r'[^.?!]+[.?!]', text))
    sentences = [match.group().strip() for match in matches]
    remainder = text[matches[-1].end():].strip() if matches else text.strip()
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

        if not current_raw_text or "no active speech" in current_raw_text.lower():
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

    if buffer_text.strip():
        capitalized = buffer_text.strip()[0].upper() + buffer_text.strip()[1:]
        full_text += capitalized + " "
        print(f"📝 Добавлен остаток буфера: {capitalized}")

    print("\n📋 Полная транскрипция:")
    final_text = full_text.strip()
    if final_text:
        final_text = final_text[0].upper() + final_text[1:]
    print(final_text)

# --- Выбор устройства перед запуском ---
selected_device_index = choose_audio_device()
sd.default.device = (selected_device_index, None)

# --- Запуск ---
print("\n🎙️ Скажите что-нибудь... (Произнесите 'стоп' для завершения)\n")

rec_thread = threading.Thread(target=record_audio)
trans_thread = threading.Thread(target=transcribe_loop)

rec_thread.start()
trans_thread.start()

rec_thread.join()
trans_thread.join()
print("✅ Завершено.")
