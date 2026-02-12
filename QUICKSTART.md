# 🚀 Быстрый старт (Шпаргалка)

## 1️⃣ Получите токены (5 минут)

### Telegram Bot Token
1. Напишите @BotFather в Telegram
2. `/newbot` → введите имя → введите username (заканчивается на `bot`)
3. Скопируйте токен

### Telegram API ID и API Hash
1. Откройте https://my.telegram.org
2. Войдите → "API development tools"
3. Скопируйте `api_id` и `api_hash`

### Yandex OAuth Token
1. Откройте https://oauth.yandex.ru/
2. "Зарегистрировать приложение" → заполните форму
3. Скопируйте ClientID
4. Откройте в браузере:
   ```
   https://oauth.yandex.ru/authorize?response_type=token&client_id=ВАШ_CLIENT_ID
   ```
5. Скопируйте `access_token` из URL

### Telegram User IDs
1. Напишите @userinfobot в Telegram
2. `/start`
3. Скопируйте ваш User ID

## 2️⃣ Настройте проект (2 минуты)

```bash
# Подключитесь к Raspberry Pi
ssh pi@raspberrypi.local

# Скопируйте проект
cd ~
# ... скопируйте все файлы в ~/telegram-video-backup

cd ~/telegram-video-backup

# Создайте .env
cp .env.example .env
nano .env
```

**Заполните .env:**
```env
TELEGRAM_BOT_TOKEN=ваш_токен
TELEGRAM_API_ID=ваш_api_id
TELEGRAM_API_HASH=ваш_api_hash
YANDEX_OAUTH_TOKEN=ваш_токен
ALLOWED_USER_IDS=123456789,987654321
TIMEZONE=Europe/Moscow
```

Сохраните: `Ctrl+O` → `Enter` → `Ctrl+X`

## 3️⃣ Запустите бота (1 минута)

```bash
# Проверьте токен (опционально)
python3 test_token.py

# Запустите
docker-compose up -d

# Проверьте логи
docker-compose logs -f
```

## 4️⃣ Используйте (30 секунд)

1. Добавьте бота в групповой чат
2. Отключите Privacy Mode через @BotFather:
   ```
   /mybots → ваш бот → Bot Settings → Group Privacy → Turn off
   ```
3. Отправьте `/start` в чат
4. Отправьте видео → получите ссылку!

## 📋 Полезные команды

```bash
# Управление
docker-compose up -d      # Запуск
docker-compose down       # Остановка
docker-compose restart    # Перезапуск
docker-compose logs -f    # Логи

# Проверка
docker-compose ps         # Статус
docker stats             # Ресурсы

# Обновление
docker-compose down
docker-compose build
docker-compose up -d
```

## 🆘 Проблемы?

```bash
# Бот не отвечает
docker-compose logs --tail=50

# Проверьте .env
cat .env

# Проверьте токен Yandex
python3 test_token.py ваш_токен

# Полный перезапуск
docker-compose down
docker-compose up -d
```

## 💡 Таймзоны

- `Europe/Moscow` - Москва (UTC+3)
- `America/New_York` - Нью-Йорк (UTC-5)
- `Asia/Tokyo` - Токио (UTC+9)

Полный список: https://en.wikipedia.org/wiki/List_of_tz_database_time_zones

---

**Подробные инструкции:** См. SETUP.md и README.md
