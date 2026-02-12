#!/usr/bin/env python3
"""
Telegram Video Backup Bot
Автоматически загружает видео из чата на Яндекс Диск
"""

import os
import logging
from datetime import datetime
from pathlib import Path
import asyncio

from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.handlers import MessageHandler

from config import Config
from yandex_disk import YandexDiskClient

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


class VideoBackupBot:
    def __init__(self):
        self.config = Config()
        self.yd_client = YandexDiskClient(self.config.yandex_token)
        self.temp_dir = Path("/tmp/telegram_videos")
        self.temp_dir.mkdir(exist_ok=True)

        self.app = Client(
            "video_backup_bot",
            api_id=self.config.telegram_api_id,
            api_hash=self.config.telegram_api_hash,
            bot_token=self.config.telegram_token,
            workdir="/app/sessions",
        )

        # Регистрируем обработчики
        self.app.on_message(filters.command("start"))(self.start)
        self.app.on_message(filters.command("stats"))(self.stats)
        self.app.on_message(filters.video & filters.group)(self.handle_video)

    async def start(self, client: Client, message: Message):
        """Команда /start"""
        await message.reply_text(
            "🎥 Видео Бэкап Бот активен!\n\n"
            "Отправьте видео, и я автоматически сохраню его на Яндекс Диск.\n"
            f"Временная зона: {self.config.timezone}"
        )

    async def handle_video(self, client: Client, message: Message):
        """Обработка входящих видео"""
        user_id = message.from_user.id
        username = message.from_user.username or message.from_user.first_name

        # Проверка разрешенных пользователей
        if user_id not in self.config.allowed_user_ids:
            logger.warning(f"Unauthorized user {user_id} (@{username}) tried to upload video")
            return

        logger.info(f"Video received from {username} (ID: {user_id})")

        video = message.video
        file_size_mb = video.file_size / (1024 * 1024)

        status_msg = await message.reply_text(
            f"⏳ Загружаю видео ({file_size_mb:.1f} MB)..."
        )

        try:
            # Определяем имя файла
            original_filename = video.file_name or f"video_{video.file_unique_id}.mp4"
            temp_file_path = self.temp_dir / original_filename

            logger.info(f"Downloading to {temp_file_path}")

            last_progress_update = [0]

            async def progress(current, total):
                percent = current * 100 / total
                # Обновляем не чаще чем каждые 10%
                if percent - last_progress_update[0] >= 10:
                    last_progress_update[0] = percent
                    try:
                        await status_msg.edit_text(
                            f"⏳ Загружаю видео ({file_size_mb:.1f} MB)...\n"
                            f"📥 Скачано: {percent:.0f}%"
                        )
                    except Exception:
                        pass

            # Скачиваем через MTProto — без лимита 20 MB
            await message.download(
                file_name=str(temp_file_path),
                progress=progress,
            )

            # Определяем папку по текущей дате
            now = datetime.now(self.config.get_timezone())
            folder_name = now.strftime("%Y-%m-%d")

            await status_msg.edit_text(
                f"⏳ Видео загружено ({file_size_mb:.1f} MB)\n"
                f"📤 Загружаю на Яндекс Диск в папку {folder_name}..."
            )

            # Загружаем на Яндекс Диск
            logger.info(f"Uploading to Yandex Disk: {folder_name}/{original_filename}")
            public_url = await self.yd_client.upload_video(
                temp_file_path,
                folder_name,
                original_filename
            )

            # Удаляем временный файл
            temp_file_path.unlink()
            logger.info(f"Temporary file deleted: {temp_file_path}")

            await status_msg.edit_text(
                f"✅ Видео успешно загружено!\n\n"
                f"📁 Папка: {folder_name}\n"
                f"Все видео за сегодня: {public_url}"
            )

            logger.info(f"Video uploaded successfully: {public_url}")

        except Exception as e:
            error_msg = str(e)
            logger.error(f"Error uploading video: {error_msg}", exc_info=True)

            await status_msg.edit_text(
                f"❌ Ошибка при загрузке видео:\n\n"
                f"{error_msg}\n\n"
                f"Попробуйте еще раз или свяжитесь с администратором."
            )

            # Уведомляем всех разрешенных пользователей
            for admin_id in self.config.allowed_user_ids:
                try:
                    await client.send_message(
                        chat_id=admin_id,
                        text=f"⚠️ Ошибка загрузки видео:\n\n"
                             f"Пользователь: {username}\n"
                             f"Файл: {original_filename if 'original_filename' in locals() else 'unknown'}\n"
                             f"Ошибка: {error_msg}"
                    )
                except Exception as notify_error:
                    logger.error(f"Failed to notify user {admin_id}: {notify_error}")

            # Очищаем временный файл если он существует
            if 'temp_file_path' in locals() and temp_file_path.exists():
                temp_file_path.unlink()

    async def stats(self, client: Client, message: Message):
        """Команда /stats — показывает статистику"""
        user_id = message.from_user.id

        if user_id not in self.config.allowed_user_ids:
            return

        try:
            stats = await self.yd_client.get_stats()
            await message.reply_text(
                f"📊 Статистика Яндекс Диска:\n\n"
                f"💾 Использовано: {stats['used_gb']:.2f} GB\n"
                f"📦 Доступно: {stats['total_gb']:.2f} GB\n"
                f"📈 Занято: {stats['used_percent']:.1f}%"
            )
        except Exception as e:
            logger.error(f"Error getting stats: {e}")
            await message.reply_text(f"❌ Ошибка получения статистики: {e}")

    def run(self):
        """Запуск бота"""
        logger.info("Starting bot...")
        self.app.run()


if __name__ == '__main__':
    bot = VideoBackupBot()
    bot.run()