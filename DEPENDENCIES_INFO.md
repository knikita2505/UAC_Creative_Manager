# 📦 Информация о зависимостях

## 🔧 Решение конфликтов зависимостей

### Проблема
При установке зависимостей возникал конфликт между пакетами:
- `googleads` требует `google-auth<2.0.0`
- `google-auth-oauthlib` требует `google-auth>=2.15.0`

### Решение
Создана упрощенная версия `requirements.txt` с базовыми зависимостями:

```txt
fastapi==0.104.1
uvicorn[standard]==0.24.0
python-multipart==0.0.6
aiofiles==23.2.1
pydantic==2.5.0
python-dotenv==1.0.0
requests>=2.25.0
pillow>=9.0.0
```

### Google API интеграции
Google API пакеты временно закомментированы в `requirements.txt`:

```txt
# Google API packages (will be added later when integrating)
# google-auth
# google-auth-oauthlib
# google-auth-httplib2
# google-api-python-client
# googleads
```

## 🚀 План интеграции Google API

### Этап 1: YouTube Data API
```bash
pip install google-api-python-client google-auth-oauthlib
```

### Этап 2: Google Ads API
```bash
# Создать отдельное виртуальное окружение для Google Ads
python3 -m venv venv_googleads
source venv_googleads/bin/activate
pip install googleads
```

### Этап 3: Универсальное решение
Использовать разные виртуальные окружения для разных API или найти альтернативные библиотеки.

## 🔄 Альтернативные решения

### 1. Разделение на микросервисы
- Backend для основной логики
- Отдельный сервис для Google API
- Отдельный сервис для YouTube загрузок

### 2. Использование Docker
Каждый сервис в отдельном контейнере с собственными зависимостями.

### 3. Альтернативные библиотеки
- `google-cloud-storage` вместо прямого использования Google APIs
- `youtube-dl` для работы с YouTube

## 📝 Текущее состояние

✅ **Работает:**
- FastAPI backend
- React frontend
- Базовый функционал загрузки
- Реестр креативов
- Управление модалками

⏳ **В разработке:**
- Google OAuth2 интеграция
- YouTube Data API
- Google Ads API
- Обработка видео (ffmpeg/opencv)

## 🛠 Рекомендации

1. **Для разработки**: Используйте текущую версию с базовыми зависимостями
2. **Для продакшена**: Разделите на микросервисы или используйте Docker
3. **Для тестирования**: Создайте отдельное окружение для Google API интеграций

## 📞 Поддержка

При возникновении проблем с зависимостями:
1. Проверьте версии Python и pip
2. Используйте виртуальные окружения
3. Рассмотрите возможность разделения на микросервисы
4. Обратитесь к документации конкретных библиотек
