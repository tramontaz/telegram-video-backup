# Используем официальный Python образ для ARM
FROM python:3.11-slim-bullseye

# Устанавливаем рабочую директорию
WORKDIR /app

# Устанавливаем gcc для сборки tgcrypto
RUN apt-get update && apt-get install -y --no-install-recommends gcc libc6-dev && rm -rf /var/lib/apt/lists/*

# Копируем файл зависимостей
COPY requirements.txt .

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Копируем код приложения
COPY bot.py .
COPY yandex_disk.py .
COPY config.py .

# Создаем директории для временных файлов и сессии Pyrogram
RUN mkdir -p /tmp/telegram_videos /app/sessions

# Запускаем бота
CMD ["python", "-u", "bot.py"]
