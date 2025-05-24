ТРАНСКРИБАЦИЯ:


--- Скачиваем на свой ПК:
1. Python3.10: https://www.python.org/downloads/release/python-31011/
2. NVIDIA CUDA Toolkit: https://developer.nvidia.com/cuda-downloads


--- Создаём виртуальное окружение:
```sh
python -m venv .venv
```


--- Входим в виртуальное окружение:
А) Через переключение версий python справа внизу VSCode с "3.10 Global" на "3.10 (.venv)"
После этого открыть новый терминал и должно появиться уведомление, что venv скрыто активирован.
Б) Если не получилось сделать А), то второй подход(aka "Каменный век"):
**Windows:**
```sh
source .venv/Scripts/activate
#иногда не работает и надо без source просто написать: .venv/Scripts/activate
```
**Linux/Mac:**
```sh
source .venv/bin/activate
```


--- Whisper и зависимости.
ВАРИАНТ А(чат гпт)):
--- Устанавливаем Pytorch перед whisperx: https://pytorch.org
```sh
# Почему именно эта версия? тип другие выдают ошибки да, но где написанно что эта окажется норм? как нагуглил?
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121  # Для GPU
```
```sh
# Почему не через pip install whisper
pip install git+https://github.com/m-bain/whisperX.git
```
```sh
pip install numpy torchaudio transformers ffmpeg-python silero-vad
```
```sh
pip install python-dotenv
```
ВАРИАНТ Б(у меня сработало):
- Установка аналогично обычному whisper:
1. Скачиваем whisperX:  pip install git+https://github.com/m-bain/whisperX.git
2. удаляем torch(потому что если сначала скачать торч не той версии, то whisper при обновлении скачет торч на cpu):   python -m pip uninstall torch
3. устанавливаем torch с CUDA:   https://pytorch.org/get-started/locally/


ДАЛЕЕ:
--- Создаём себе Токен Hugging Face для скачивания модели для диаризации спикера:
1. Создаём аккаунт на HuggingFace.
2. Идём в Настройки => Access Tokens(https://huggingface.co/settings/tokens) => Create new token =>
{
Token name = whisperx
Все галочки оставьте в изначальном состоянии
В "Repositories permissions" добавьте: pyannote/speaker-diarization-3.1 и pyannote/segmentation-3.0
}
=> CreateToken => Скопирывать токен и сохранить его куда-нибудь.
3. Получить доступ к моделям. Надо зайти на каждую из ссылок и получить доступ к моделям(для этого заполнить данные вверху страницы).
3.1 https://huggingface.co/pyannote/segmentation-3.0
3.2 https://huggingface.co/pyannote/speaker-diarization-3.1
4. Создаём в проекте в корневом каталоге файл с названием ".env"
Вставляем в него строку:
```python
HUGGINGFACE_TOKEN="hf_..."
```
5. Вставьте в "" свой токен.



--- Установка cuDNN
1. Авторизуйтесь на сайте **NVIDIA**
2. Перейдите в раздел архива и скачайте **cuDNN v8.9.6**:
   🔗 [Скачать cuDNN v8.9.6](https://developer.nvidia.com/rdp/cudnn-archive)
3. Распакуйте архив и скопируйте файлы в соответствующие папки:
| Папка в архиве | Куда скопировать |
|---------------|----------------|
| **bin/** | `C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v12.8\bin` |
| **lib/** | `C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v12.8\lib\x64` |
| **include/** | `C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v12.8\include` |





---

## Добавление аудиофайла
Скопируйте аудиофайл в рабочую папку и укажите его название в коде **transcriber.py**.

---

## Настройка скрипта:
Выставьте настройки в transcriber.py:
Те, что в подпунктах: "установи значения перед запуском" и "зависит от устройства".












ГЕНЕРАЦИЯ ПРОТОКОЛА:


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

