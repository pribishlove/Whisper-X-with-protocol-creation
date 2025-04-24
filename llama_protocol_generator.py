from llama_cpp import Llama
import json

# Загрузка модели с GPU
llm = Llama(
    model_path="models/llama-2-7b-chat.Q4_K_M.gguf",
    n_ctx=2048,
    n_gpu_layers=35,  # Подстрой под свою видеокарту
    n_threads=6
)

# Загрузка текста
with open("TEXT_after_transcription/transcription_output.json", "r", encoding="utf-8") as f:
    data = json.load(f)

full_text = "\n".join([f"[{s.get('start', 0):.2f}s] {s.get('text', '')}" for s in data["segments"]])
chunk_size = 1500
chunks = [full_text[i:i+chunk_size] for i in range(0, len(full_text), chunk_size)]

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

full_protocol = "\n\n".join(protocol_parts)

with open("TEXT_after_transcription/protocol_output.txt", "w", encoding="utf-8") as f:
    f.write(full_protocol)

print("Протокол совещания сохранён в 'protocol_output.txt'")
