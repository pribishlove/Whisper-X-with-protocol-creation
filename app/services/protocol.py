import time
from llama_cpp import Llama
from app.core.config import settings

def run_llama_protocol(transcribed_text: str) -> str:
    start = time.time()

    llm = Llama(
        model_path=str(settings.MODEL_PATH),
        n_ctx=16384,
        n_gpu_layers=35,
        n_threads=6,
        chat_format="llama-3"
    )

    response = llm.create_chat_completion(
        messages=[
            {"role": "system", "content": "Ты помощник, который составляет краткий и информативный протокол по тексту совещания."},
            {"role": "user", "content": f"Вот стенограмма совещания:\n\n{transcribed_text}\n\nСоставь краткий протокол по тексту выше на русском языке."}
        ],
        max_tokens=2048,
        temperature=0.3
    )

    print(f"✅ Protocol generated in {time.time() - start:.2f} seconds")
    return response["choices"][0]["message"]["content"].strip()
