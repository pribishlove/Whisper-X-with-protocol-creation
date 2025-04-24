from llama_cpp import Llama

# Загрузка модели LLaMA 3.1 с поддержкой chat-формата
llm = Llama(
    model_path="models/llama-3-8B-Instruct.Q4_K_M.gguf",
    n_ctx=16384,              # Убедись, что весь текст помещается в контекст
    n_gpu_layers=35,         # Под твою RTX 4060 Ti (8 GB)
    n_threads=6,
    chat_format="llama-3"
)

# Загрузка текста стенограммы
with open("TEXT_after_transcription/transcription_output.txt", "r", encoding="utf-8") as f:
    full_text = f.read()

# Генерация протокола по полному тексту
response = llm.create_chat_completion(
    messages=[
        {"role": "system", "content": "Ты помощник, который составляет краткий и информативный протокол по тексту совещания."},
        {"role": "user", "content": f"Вот стенограмма совещания:\n\n{full_text}\n\nСоставь краткий протокол по тексту выше на русском языке."}
    ],
    max_tokens=2048,
    temperature=0.3
)

# Извлекаем результат
protocol = response["choices"][0]["message"]["content"].strip()

# Сохраняем протокол
with open("TEXT_after_transcription/protocol_output.txt", "w", encoding="utf-8") as f:
    f.write(protocol)

print("Протокол совещания сохранён в 'protocol_output.txt'")
