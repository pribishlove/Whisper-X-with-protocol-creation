# Используем официальный образ Python
FROM python:3.10.17-slim-bookworm

# Устанавливаем рабочую директорию
WORKDIR /app

# Устанавливаем системные зависимости
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --upgrade pip && \
	pip install --no-cache-dir -r requirements.txt

COPY . .

# Открываем нужный порт (если требуется)
EXPOSE 8000

# Команда запуска (замените на вашу)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
