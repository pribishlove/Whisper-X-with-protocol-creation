from llama_cpp import Llama
import json

# Загрузка модели
llm = Llama(model_path="models/llama-2-7b-chat.Q4_K_M.gguf", n_ctx=2048)

# Загружаем текст после транскрибации
with open("TEXT_after_transcription/transcription_output.json", "r", encoding="utf-8") as f:
    data = json.load(f)

# Формируем текст
full_text = "\n".join([f"[{s.get('start', 0):.2f}s] {s.get('text', '')}" for s in data["segments"]])

# Разбиваем текст на чанки (например, по 1500 символов)
chunk_size = 1500
chunks = [full_text[i:i+chunk_size] for i in range(0, len(full_text), chunk_size)]

# Формируем протокол
protocol_parts = []
for chunk in chunks:
    prompt = (
        "Ниже приведён фрагмент стенограммы совещания. Составь краткий протокол: \n\n"
        f"{chunk}\n\n"
        "Протокол:"
    )
    response = llm(prompt, max_tokens=1024, stop=["\n\n", "###"])
    text = response["choices"][0]["text"].strip()
    protocol_parts.append(text)

# Объединяем итог
full_protocol = "\n\n".join(protocol_parts)

# Сохраняем
with open("TEXT_after_transcription/protocol_output.txt", "w", encoding="utf-8") as f:
    f.write(full_protocol)

print("Протокол совещания сохранён в 'protocol_output.txt'")
