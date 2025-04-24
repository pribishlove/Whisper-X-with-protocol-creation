(для гайда по запуску transcriber.py смотри наш основной репозиторий с транскрибацией)
**Для запуска llama_protocol_generator.py нужно:**
0. Виртуальное окружение: python -m venv .venv

1. В виртуальном окружении в консоль ввести:
```bash
$env:CMAKE_ARGS="-DLLAMA_CUDA=on" #создать переменную окружения
pip install llama-cpp-python --force-reinstall --upgrade --no-cache-dir --verbose #установить llama-cpp
```
Будет долгое скачивание и установка(минут 10-15)

2. Скачать модель с сайта.
Заходите на сайт https://huggingface.co/mradermacher/llama-3-8B-Instruct-GGUF 
и в таблице выбираете модель для скачивания ([таблица с сайта](https://huggingface.co/mradermacher/llama-3-8B-Instruct-GGUF#provided-quants))

Можно экспеременитровать с разными моделями. Мы выбрали для начала из рекомендованных эту: Q4_K_M	

3. Скаченную модель переместить в папку models в корневом каталоге.

4. В скрипте llama_protocol_generator.py надо побаловаться с параметрами.
llm = Llama(
    model_path="models/llama-3-8B-Instruct.Q4_K_M.gguf",
    n_ctx=16384,              # Убедись, что весь текст помещается в контекст
    n_gpu_layers=35,         # Под твою RTX 4060 Ti (8 GB)
    n_threads=6,
    chat_format="llama-3"
)
- как минимум указать версию скаченной модели(если вы скачать отличную от указанной в скрипте)
- в зависимсоти от размера текста понадобится изменить context(n_ctx): больше контекст - больше слов может обработать в запросе, но уменьшается скорость.

5. В TEXT_after_transcrption поместите ваш текст после транскрибации в transcription_oitput.txt

6. Имзенить промпт внутри скрипта для ваших целей.
Готово. Запускайте llama_protocol_generator.py

