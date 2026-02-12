"""
Клиент для работы с Яндекс Диском
"""

import logging
import aiohttp
import asyncio
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


class YandexDiskClient:
    """Асинхронный клиент для Яндекс Диска"""
    
    BASE_URL = "https://cloud-api.yandex.net/v1/disk"
    
    ROOT_FOLDER = "Alisa"

    def __init__(self, oauth_token: str):
        self.oauth_token = oauth_token
        self.headers = {
            "Authorization": f"OAuth {oauth_token}",
            "Content-Type": "application/json"
        }
        self._folder_cache = {}  # Кэш созданных папок
    
    async def _make_request(self, method: str, url: str, **kwargs) -> dict:
        """Выполняет HTTP запрос к API"""
        async with aiohttp.ClientSession() as session:
            async with session.request(
                method, url, headers=self.headers, **kwargs
            ) as response:
                if response.status >= 400:
                    error_text = await response.text()
                    raise Exception(
                        f"Yandex Disk API error [{response.status}]: {error_text}"
                    )
                return await response.json()
    
    async def create_folder(self, folder_path: str) -> bool:
        """Создает папку на Яндекс Диске (если не существует)"""
        # Проверяем кэш
        if folder_path in self._folder_cache:
            logger.info(f"Folder {folder_path} already exists (cached)")
            return False
        
        try:
            url = f"{self.BASE_URL}/resources"
            params = {"path": folder_path}
            
            await self._make_request("PUT", url, params=params)
            logger.info(f"Folder created: {folder_path}")
            self._folder_cache[folder_path] = True
            return True
            
        except Exception as e:
            error_msg = str(e)
            # Если папка уже существует - это не ошибка
            if "DiskPathPointsToExistentDirectoryError" in error_msg:
                logger.info(f"Folder already exists: {folder_path}")
                self._folder_cache[folder_path] = True
                return False
            raise
    
    async def upload_file(self, local_path: Path, remote_path: str) -> str:
        """
        Загружает файл на Яндекс Диск
        
        Args:
            local_path: Локальный путь к файлу
            remote_path: Путь на Яндекс Диске (например, "2024-01-15/video.mp4")
        
        Returns:
            URL для загрузки
        """
        # Получаем URL для загрузки
        url = f"{self.BASE_URL}/resources/upload"
        params = {
            "path": remote_path,
            "overwrite": "false"  # Не перезаписываем существующие файлы
        }
        
        logger.info(f"Getting upload URL for {remote_path}")
        upload_info = await self._make_request("GET", url, params=params)
        upload_url = upload_info["href"]
        logger.info(f"Got upload URL, starting upload...")

        file_size = local_path.stat().st_size
        timeout = aiohttp.ClientTimeout(total=1800, sock_connect=30, sock_read=300)
        logger.info(f"Uploading {file_size / (1024*1024):.1f} MB to {upload_url[:80]}...")

        async with aiohttp.ClientSession(timeout=timeout) as session:
            with open(local_path, 'rb') as f:
                async with session.put(upload_url, data=f) as response:
                    if response.status >= 400:
                        error_text = await response.text()
                        raise Exception(
                            f"Upload failed [{response.status}]: {error_text}"
                        )

        logger.info(f"File uploaded: {remote_path}")
        return upload_url
    
    async def publish_folder(self, folder_path: str) -> str:
        """
        Делает папку публичной и возвращает публичную ссылку
        
        Args:
            folder_path: Путь к папке на Яндекс Диске
        
        Returns:
            Публичная ссылка на папку
        """
        url = f"{self.BASE_URL}/resources/publish"
        params = {"path": folder_path}
        
        try:
            await self._make_request("PUT", url, params=params)
            logger.info(f"Folder published: {folder_path}")
        except Exception as e:
            if "DiskResourceAlreadyPublishedError" not in str(e):
                raise
            logger.info(f"Folder already published: {folder_path}")

        # Получаем публичную ссылку
        return await self.get_public_url(folder_path)
    
    async def get_public_url(self, folder_path: str) -> str:
        """Получает публичную ссылку на ресурс"""
        url = f"{self.BASE_URL}/resources"
        params = {"path": folder_path}
        
        result = await self._make_request("GET", url, params=params)
        
        if "public_url" not in result:
            raise Exception(f"Folder {folder_path} is not published")
        
        return result["public_url"]
    
    async def upload_video(
        self, 
        local_path: Path, 
        folder_name: str, 
        filename: str
    ) -> str:
        """
        Загружает видео в папку по дате и возвращает публичную ссылку на папку
        
        Args:
            local_path: Локальный путь к видео файлу
            folder_name: Название папки (обычно дата YYYY-MM-DD)
            filename: Имя файла на диске
        
        Returns:
            Публичная ссылка на папку
        """
        # Создаем корневую папку и подпапку по дате
        await self.create_folder(self.ROOT_FOLDER)
        date_folder = f"{self.ROOT_FOLDER}/{folder_name}"
        await self.create_folder(date_folder)

        # Загружаем файл
        remote_path = f"{date_folder}/{filename}"
        await self.upload_file(local_path, remote_path)

        # Публикуем папку и получаем ссылку
        public_url = await self.publish_folder(date_folder)
        
        return public_url
    
    async def get_stats(self) -> dict:
        """Получает статистику использования диска"""
        url = f"{self.BASE_URL}/"
        result = await self._make_request("GET", url)
        
        total_space = result.get("total_space", 0)
        used_space = result.get("used_space", 0)
        
        return {
            "total_gb": total_space / (1024 ** 3),
            "used_gb": used_space / (1024 ** 3),
            "used_percent": (used_space / total_space * 100) if total_space > 0 else 0
        }
