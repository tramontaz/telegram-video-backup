"""
Конфигурация бота
"""

import os
from pathlib import Path
from typing import List
import pytz
from dotenv import load_dotenv

# Загружаем переменные окружения из .env файла
load_dotenv()


class Config:
    """Конфигурация приложения"""
    
    def __init__(self):
        # Telegram Bot Token
        self.telegram_token = os.getenv("TELEGRAM_BOT_TOKEN")
        if not self.telegram_token:
            raise ValueError("TELEGRAM_BOT_TOKEN not set in environment")

        # Telegram API credentials (from https://my.telegram.org)
        api_id = os.getenv("TELEGRAM_API_ID")
        if not api_id:
            raise ValueError("TELEGRAM_API_ID not set in environment")
        self.telegram_api_id = int(api_id)

        self.telegram_api_hash = os.getenv("TELEGRAM_API_HASH")
        if not self.telegram_api_hash:
            raise ValueError("TELEGRAM_API_HASH not set in environment")
        
        # Yandex Disk OAuth Token
        self.yandex_token = os.getenv("YANDEX_OAUTH_TOKEN")
        if not self.yandex_token:
            raise ValueError("YANDEX_OAUTH_TOKEN not set in environment")
        
        # Разрешенные пользователи (ID через запятую)
        allowed_users_str = os.getenv("ALLOWED_USER_IDS", "")
        if not allowed_users_str:
            raise ValueError("ALLOWED_USER_IDS not set in environment")
        
        self.allowed_user_ids = [
            int(user_id.strip()) 
            for user_id in allowed_users_str.split(",")
        ]
        
        # Временная зона
        self.timezone = os.getenv("TIMEZONE", "Europe/Moscow")
        try:
            pytz.timezone(self.timezone)
        except pytz.exceptions.UnknownTimeZoneError:
            raise ValueError(f"Unknown timezone: {self.timezone}")
    
    def get_timezone(self):
        """Возвращает объект timezone"""
        return pytz.timezone(self.timezone)
    
    def __repr__(self):
        return (
            f"Config(timezone={self.timezone}, "
            f"allowed_users={len(self.allowed_user_ids)})"
        )
