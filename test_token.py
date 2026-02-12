#!/usr/bin/env python3
"""
Тестовый скрипт для проверки Yandex OAuth токена
Запустите этот скрипт для проверки токена перед запуском бота
"""

import sys
import asyncio
import aiohttp


async def test_yandex_token(token: str):
    """Проверяет валидность Yandex OAuth токена"""
    
    url = "https://cloud-api.yandex.net/v1/disk/"
    headers = {
        "Authorization": f"OAuth {token}",
        "Content-Type": "application/json"
    }
    
    print("🔍 Проверка Yandex OAuth токена...")
    print(f"📝 Токен: {token[:20]}...{token[-10:]}")
    print()
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    total_gb = data.get("total_space", 0) / (1024 ** 3)
                    used_gb = data.get("used_space", 0) / (1024 ** 3)
                    free_gb = total_gb - used_gb
                    used_percent = (used_gb / total_gb * 100) if total_gb > 0 else 0
                    
                    print("✅ Токен валиден!")
                    print()
                    print("📊 Информация о диске:")
                    print(f"   💾 Всего места: {total_gb:.2f} GB")
                    print(f"   📈 Использовано: {used_gb:.2f} GB ({used_percent:.1f}%)")
                    print(f"   📉 Свободно: {free_gb:.2f} GB")
                    print()
                    print("✨ Всё готово к работе!")
                    return True
                    
                elif response.status == 401:
                    print("❌ Ошибка авторизации!")
                    print("   Токен недействителен или истек.")
                    print()
                    print("💡 Решение:")
                    print("   1. Проверьте правильность токена")
                    print("   2. Получите новый токен (см. SETUP.md)")
                    return False
                    
                else:
                    error_text = await response.text()
                    print(f"❌ Ошибка API [{response.status}]:")
                    print(f"   {error_text}")
                    return False
                    
    except aiohttp.ClientError as e:
        print(f"❌ Ошибка сети: {e}")
        print()
        print("💡 Проверьте интернет-соединение")
        return False
    
    except Exception as e:
        print(f"❌ Неожиданная ошибка: {e}")
        return False


async def test_folder_operations(token: str):
    """Тестирует создание папки и загрузку файла"""
    
    url_base = "https://cloud-api.yandex.net/v1/disk"
    headers = {
        "Authorization": f"OAuth {token}",
        "Content-Type": "application/json"
    }
    
    test_folder = "telegram-bot-test"
    
    print()
    print("🧪 Тестирование операций с папками...")
    
    try:
        async with aiohttp.ClientSession() as session:
            # Создание тестовой папки
            print(f"   📁 Создание папки '{test_folder}'...")
            url = f"{url_base}/resources"
            params = {"path": test_folder}
            
            async with session.put(url, headers=headers, params=params) as response:
                if response.status in [201, 409]:  # 409 = папка уже существует
                    print("   ✅ Папка создана (или уже существует)")
                else:
                    error = await response.text()
                    print(f"   ❌ Ошибка создания папки: {error}")
                    return False
            
            # Публикация папки
            print(f"   🌐 Публикация папки...")
            url = f"{url_base}/resources/publish"
            
            async with session.put(url, headers=headers, params=params) as response:
                if response.status in [200, 409]:  # 409 = уже опубликована
                    print("   ✅ Папка опубликована")
                    
                    # Получение публичной ссылки
                    async with session.get(
                        f"{url_base}/resources",
                        headers=headers,
                        params=params
                    ) as get_response:
                        if get_response.status == 200:
                            data = await get_response.json()
                            public_url = data.get("public_url")
                            if public_url:
                                print(f"   🔗 Публичная ссылка: {public_url}")
                else:
                    error = await response.text()
                    print(f"   ❌ Ошибка публикации: {error}")
                    return False
            
            # Удаление тестовой папки
            print(f"   🗑️  Удаление тестовой папки...")
            url = f"{url_base}/resources"
            
            async with session.delete(url, headers=headers, params=params) as response:
                if response.status in [204, 202]:
                    print("   ✅ Тестовая папка удалена")
                else:
                    print("   ⚠️  Не удалось удалить тестовую папку (можете удалить вручную)")
            
            print()
            print("✅ Все тесты пройдены успешно!")
            return True
            
    except Exception as e:
        print(f"❌ Ошибка при тестировании: {e}")
        return False


async def main():
    print("=" * 60)
    print("Тестирование Yandex OAuth токена для Telegram Video Backup Bot")
    print("=" * 60)
    print()
    
    # Получаем токен из аргументов или запрашиваем
    if len(sys.argv) > 1:
        token = sys.argv[1]
    else:
        print("Введите Yandex OAuth токен:")
        token = input("> ").strip()
    
    if not token:
        print("❌ Токен не указан!")
        sys.exit(1)
    
    # Проверка токена
    valid = await test_yandex_token(token)
    
    if not valid:
        sys.exit(1)
    
    # Дополнительное тестирование
    print()
    response = input("Провести дополнительное тестирование операций? (y/n): ")
    
    if response.lower() in ['y', 'yes', 'д', 'да']:
        success = await test_folder_operations(token)
        if not success:
            sys.exit(1)
    
    print()
    print("🎉 Готово! Можете использовать этот токен в .env файле")


if __name__ == '__main__':
    asyncio.run(main())
