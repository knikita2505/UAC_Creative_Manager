#!/usr/bin/env python3
"""
Скрипт для инициализации базы данных Supabase
"""

import asyncio
import sys
from pathlib import Path
from database import db_manager
from config import SUPABASE_URL, SUPABASE_KEY

async def init_database():
    """Инициализация базы данных"""
    print("🚀 Инициализация базы данных UAC Creative Manager...")
    
    try:
        # Проверка подключения к Supabase
        print("📡 Проверка подключения к Supabase...")
        print(f"   URL: {SUPABASE_URL}")
        print(f"   Key: {SUPABASE_KEY[:20]}...")
        
        # Создание ролей по умолчанию
        print("👥 Создание ролей по умолчанию...")
        await db_manager.create_default_roles()
        
        # Получение списка ролей для проверки
        roles = await db_manager.get_roles()
        print(f"✅ Создано ролей: {len(roles)}")
        for role in roles:
            print(f"   - {role['name']}: {role['description']}")
        
        # Логирование инициализации
        await db_manager.create_log(
            "database_initialized",
            {"message": "Database initialized successfully", "roles_count": len(roles)}
        )
        
        print("✅ База данных успешно инициализирована!")
        
    except Exception as e:
        print(f"❌ Ошибка инициализации базы данных: {e}")
        sys.exit(1)

async def test_connections():
    """Тестирование подключений"""
    print("\n🧪 Тестирование подключений...")
    
    try:
        # Тест получения ролей
        roles = await db_manager.get_roles()
        print(f"✅ Роли: {len(roles)} записей")
        
        # Тест получения модалок
        modals = await db_manager.get_modal_images()
        print(f"✅ Модалки: {len(modals)} записей")
        
        # Тест получения шаблонов
        templates = await db_manager.get_templates()
        print(f"✅ Шаблоны: {len(templates)} записей")
        
        # Тест получения загрузок
        uploads = await db_manager.get_uploads()
        print(f"✅ Загрузки: {len(uploads)} записей")
        
        print("✅ Все тесты подключений прошли успешно!")
        
    except Exception as e:
        print(f"❌ Ошибка тестирования подключений: {e}")
        sys.exit(1)

if __name__ == "__main__":
    print("🎯 UAC Creative Manager - Инициализация базы данных")
    print("=" * 50)
    
    # Запуск инициализации
    asyncio.run(init_database())
    
    # Тестирование подключений
    asyncio.run(test_connections())
    
    print("\n🎉 Готово! База данных настроена и готова к работе.")
