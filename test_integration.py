#!/usr/bin/env python3
"""
Тестовый скрипт для проверки интеграции загрузки видео на YouTube
"""
import asyncio
import httpx
import json
from pathlib import Path

async def test_youtube_integration():
    """Тестирование YouTube интеграции"""
    base_url = "http://localhost:8000"
    
    async with httpx.AsyncClient() as client:
        print("🧪 Тестирование YouTube интеграции...")
        
        # 1. Проверка статуса интеграций
        print("\n1. Проверка статуса интеграций...")
        try:
            response = await client.get(f"{base_url}/integrations/status")
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Статус интеграций получен: {data}")
            else:
                print(f"❌ Ошибка получения статуса: {response.status_code}")
        except Exception as e:
            print(f"❌ Ошибка подключения: {e}")
            return
        
        # 2. Проверка настроек YouTube
        print("\n2. Проверка настроек YouTube...")
        try:
            response = await client.get(f"{base_url}/integrations/settings")
            if response.status_code == 200:
                data = response.json()
                youtube_settings = data.get("settings", {}).get("youtube", {})
                print(f"✅ Настройки YouTube: {youtube_settings}")
                
                if youtube_settings.get("client_id"):
                    print("✅ YouTube credentials настроены")
                else:
                    print("⚠️ YouTube credentials не настроены")
            else:
                print(f"❌ Ошибка получения настроек: {response.status_code}")
        except Exception as e:
            print(f"❌ Ошибка получения настроек: {e}")
        
        # 3. Тестирование подключения к YouTube
        print("\n3. Тестирование подключения к YouTube...")
        try:
            response = await client.post(f"{base_url}/integrations/youtube/test")
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    print(f"✅ YouTube подключение успешно: {data.get('message')}")
                else:
                    print(f"⚠️ YouTube подключение не удалось: {data.get('error')}")
            else:
                print(f"❌ Ошибка тестирования YouTube: {response.status_code}")
        except Exception as e:
            print(f"❌ Ошибка тестирования YouTube: {e}")
        
        # 4. Проверка модалок
        print("\n4. Проверка модалок...")
        try:
            response = await client.get(f"{base_url}/modals")
            if response.status_code == 200:
                data = response.json()
                modals = data.get("modals", [])
                print(f"✅ Найдено модалок: {len(modals)}")
                for modal in modals:
                    print(f"   - {modal['filename']} (ID: {modal['id']})")
            else:
                print(f"❌ Ошибка получения модалок: {response.status_code}")
        except Exception as e:
            print(f"❌ Ошибка получения модалок: {e}")
        
        # 5. Проверка загрузок
        print("\n5. Проверка загрузок...")
        try:
            response = await client.get(f"{base_url}/uploads")
            if response.status_code == 200:
                data = response.json()
                uploads = data.get("uploads", [])
                print(f"✅ Найдено загрузок: {len(uploads)}")
                for upload in uploads:
                    print(f"   - {upload['campaign_name']} - {upload['youtube_url']}")
            else:
                print(f"❌ Ошибка получения загрузок: {response.status_code}")
        except Exception as e:
            print(f"❌ Ошибка получения загрузок: {e}")

async def test_upload_simulation():
    """Симуляция загрузки видео"""
    base_url = "http://localhost:8000"
    
    print("\n🎬 Симуляция загрузки видео...")
    
    # Создаем тестовый видео файл
    test_video_path = Path("test_video.mp4")
    if not test_video_path.exists():
        print("⚠️ Тестовый видео файл не найден. Создаем заглушку...")
        test_video_path.write_bytes(b"fake video content")
    
    async with httpx.AsyncClient() as client:
        try:
            # Подготавливаем данные для загрузки
            files = {"video_file": open(test_video_path, "rb")}
            data = {
                "campaign_name": "Тестовая кампания",
                "video_source": "local",
                "thumbnail_option": "none"
            }
            
            print("📤 Отправка запроса на загрузку...")
            response = await client.post(
                f"{base_url}/upload/video",
                files=files,
                data=data
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get("success"):
                    print(f"✅ Загрузка успешна!")
                    print(f"   - ID: {result.get('upload_id')}")
                    print(f"   - Название: {result.get('video_title')}")
                    print(f"   - YouTube URL: {result.get('youtube_url')}")
                else:
                    print(f"❌ Ошибка загрузки: {result.get('error')}")
            else:
                print(f"❌ HTTP ошибка: {response.status_code}")
                print(f"   Ответ: {response.text}")
                
        except Exception as e:
            print(f"❌ Ошибка загрузки: {e}")
        finally:
            # Удаляем тестовый файл
            if test_video_path.exists():
                test_video_path.unlink()

async def main():
    """Основная функция тестирования"""
    print("🚀 Запуск тестирования UAC Creative Manager")
    print("=" * 50)
    
    await test_youtube_integration()
    await test_upload_simulation()
    
    print("\n" + "=" * 50)
    print("✅ Тестирование завершено!")

if __name__ == "__main__":
    asyncio.run(main())
