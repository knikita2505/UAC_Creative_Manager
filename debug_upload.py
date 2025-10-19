#!/usr/bin/env python3
"""
Скрипт для отладки загрузки видео
"""
import asyncio
import httpx
import json

async def debug_upload():
    """Отладка загрузки видео"""
    async with httpx.AsyncClient() as client:
        # Создаем тестовый файл
        with open('debug_test.mp4', 'wb') as f:
            f.write(b'fake video content for debugging')
        
        try:
            print("🔍 Отправка запроса на загрузку...")
            
            # Подготавливаем данные
            files = {'video_file': open('debug_test.mp4', 'rb')}
            data = {
                'campaign_name': 'Debug Test',
                'video_source': 'local',
                'thumbnail_option': 'first_frame'
            }
            
            print(f"📤 Данные: {data}")
            print(f"📁 Файл: debug_test.mp4")
            
            # Отправляем запрос
            response = await client.post(
                'http://localhost:8000/upload/video',
                files=files,
                data=data,
                timeout=30.0
            )
            
            print(f"📊 Статус ответа: {response.status_code}")
            print(f"📄 Заголовки: {dict(response.headers)}")
            print(f"📝 Тело ответа: {response.text}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Успех: {result}")
            else:
                print(f"❌ Ошибка HTTP: {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"❌ Детали ошибки: {error_data}")
                except:
                    print(f"❌ Текст ошибки: {response.text}")
                    
        except Exception as e:
            print(f"💥 Исключение: {e}")
            import traceback
            traceback.print_exc()
        finally:
            import os
            if os.path.exists('debug_test.mp4'):
                os.remove('debug_test.mp4')

if __name__ == "__main__":
    asyncio.run(debug_upload())
