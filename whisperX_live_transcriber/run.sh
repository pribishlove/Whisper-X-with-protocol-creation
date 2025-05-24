#!/bin/bash

# Создание виртуального окружения
python3 -m venv venv
source venv/bin/activate

# Обновление pip
pip install --upgrade pip

# Установка зависимостей
pip install -r requirements.txt

# Запуск приложения
# python live_whisperx_transcriber.py

# Актуальные версии библиотек
# pip freeze

# Удалить старое окружение
# rm -rf venv

# chmod +x run.sh
# ./run.sh