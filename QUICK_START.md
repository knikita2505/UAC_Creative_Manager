# 🚀 Быстрый старт UAC Creative Manager

## 📋 Предварительные требования

- **Python 3.8+** с pip
- **Node.js 16+** с npm
- **Git** для клонирования репозитория

## 🎯 Запуск проекта

### Вариант 1: Локальный запуск (рекомендуется для разработки)

#### 1. Запуск Backend (FastAPI)

```bash
# Сделать скрипт исполняемым (если еще не сделано)
chmod +x start-backend.sh

# Запуск backend
./start-backend.sh
```

Backend будет доступен по адресу: http://localhost:8000

#### 2. Запуск Frontend (React)

```bash
# В новом терминале
chmod +x start-frontend.sh

# Запуск frontend
./start-frontend.sh
```

Frontend будет доступен по адресу: http://localhost:3000

### Вариант 2: Docker (рекомендуется для продакшена)

```bash
# Запуск всех сервисов
docker-compose up --build

# Или в фоновом режиме
docker-compose up -d --build
```

## 🔧 Настройка

### 1. Google OAuth2

1. Перейдите в [Google Cloud Console](https://console.cloud.google.com/)
2. Создайте новый проект или выберите существующий
3. Включите YouTube Data API v3 и Google Ads API
4. Создайте OAuth2 credentials
5. Добавьте `http://localhost:8000/auth/callback` в разрешенные URI

### 2. Telegram Bot

1. Найдите [@BotFather](https://t.me/botfather) в Telegram
2. Создайте нового бота командой `/newbot`
3. Получите токен бота
4. Узнайте Chat ID для уведомлений

### 3. Supabase

1. Создайте проект в [Supabase](https://supabase.com/)
2. Получите URL и API ключ
3. Создайте таблицы (будут созданы автоматически)

## 📱 Использование

### 1. Загрузка модалок

1. Перейдите в раздел "Модалки"
2. Загрузите изображения модалок (JPG, PNG, GIF, WebP)
3. Модалки будут доступны при создании креативов

### 2. Загрузка видео

1. Перейдите в раздел "Загрузка видео"
2. Введите название кампании
3. Выберите источник видео (локальный файл или Google Drive)
4. Настройте миниатюру (без изменений, первый кадр, или с модалкой)
5. Нажмите "Загрузить на YouTube"

### 3. Просмотр реестра

1. Перейдите в раздел "Реестр креативов"
2. Просматривайте все загрузки с фильтрацией по статусу
3. Экспортируйте данные в CSV

### 4. Настройки

1. Перейдите в раздел "Настройки"
2. Настройте OAuth2, Telegram, Supabase
3. Включите мониторинг креативов

## 🐛 Решение проблем

### Backend не запускается

```bash
# Проверьте Python версию
python3 --version

# Установите зависимости вручную
cd backend
pip install -r requirements.txt
python main.py
```

### Frontend не запускается

```bash
# Проверьте Node.js версию
node --version
npm --version

# Очистите кэш и переустановите зависимости
cd frontend
rm -rf node_modules package-lock.json
npm install
npm start
```

### CORS ошибки

Убедитесь, что backend запущен на порту 8000, а frontend на порту 3000.

## 📊 API Документация

После запуска backend, документация API доступна по адресу:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 🔄 Обновление

```bash
# Получить последние изменения
git pull origin main

# Перезапустить сервисы
docker-compose down
docker-compose up --build
```

## 📞 Поддержка

При возникновении проблем:
1. Проверьте логи в консоли
2. Убедитесь, что все зависимости установлены
3. Проверьте настройки в разделе "Настройки"
4. Создайте issue в репозитории
