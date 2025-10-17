# 🎯 UAC Creative Manager

Платформа автоматизации видео-креативов под Google Ads для продвижения мобильных приложений.

## 🚀 Быстрый старт

### Backend (FastAPI)

```bash
cd backend
python3 -m pip install -r requirements.txt
python3 main.py
```

Backend будет доступен по адресу: http://localhost:8000

### Frontend (React)

```bash
cd frontend
npm install
npm start
```

Frontend будет доступен по адресу: http://localhost:3000

### Автоматический запуск

```bash
# Backend
./start-backend.sh

# Frontend (в новом терминале)
./start-frontend.sh
```

> **Примечание**: Если возникают проблемы с зависимостями, см. [SETUP_INSTRUCTIONS.md](SETUP_INSTRUCTIONS.md)

## 📦 Основные функции

### ✅ Реализовано

- **Загрузка видео на YouTube** с очисткой метаданных и уникализацией
- **Система выбора миниатюр** (3 варианта: без изменений, первый кадр, кастомная модалка)
- **Управление модалками** - загрузка и выбор изображений для наложения
- **Реестр креативов** - отслеживание всех загрузок с фильтрацией и экспортом
- **Настройки** - конфигурация OAuth, Telegram, базы данных и мониторинга

### 🔄 В разработке

- Интеграция с Google OAuth2
- Интеграция с YouTube Data API
- Интеграция с Google Ads API
- Мониторинг заблокированных креативов
- AI-анализ креативов
- Автоматическая перезагрузка

## 🛠 Технологии

- **Frontend**: React + TailwindCSS
- **Backend**: FastAPI (Python)
- **База данных**: Supabase (PostgreSQL)
- **Интеграции**: Google OAuth2, YouTube API, Google Ads API, Telegram Bot

## 📁 Структура проекта

```
UAC_Creative_Manager/
├── backend/                 # FastAPI backend
│   ├── main.py             # Основной файл API
│   └── requirements.txt    # Python зависимости
├── frontend/               # React frontend
│   ├── src/
│   │   ├── components/    # React компоненты
│   │   ├── App.js         # Главный компонент
│   │   └── index.js       # Точка входа
│   ├── package.json       # Node.js зависимости
│   └── tailwind.config.js # TailwindCSS конфигурация
└── README.md              # Документация
```

## 🔧 Настройка

1. **Google OAuth2**: Настройте OAuth2 в Google Cloud Console
2. **Telegram Bot**: Создайте бота через @BotFather
3. **Supabase**: Настройте проект в Supabase
4. **YouTube API**: Включите YouTube Data API v3

## 📝 API Endpoints

### Загрузка видео
- `POST /upload/video` - Загрузка видео на YouTube
- `POST /upload/modal` - Загрузка изображения модалки
- `GET /modals` - Получение списка модалок

### Реестр
- `GET /uploads` - Получение списка загрузок
- `GET /templates` - Получение списка шаблонов

## 🎨 Интерфейс

Платформа имеет современный и удобный интерфейс с 4 основными разделами:

1. **Загрузка видео** - Основной функционал загрузки
2. **Реестр креативов** - Просмотр и управление загрузками
3. **Модалки** - Управление изображениями для наложения
4. **Настройки** - Конфигурация интеграций

## 🔮 Планы развития

- Автоматическое добавление в кампании Google Ads
- AI-анализ креативов с определением стиля и агрессивности
- Автоматическая перезагрузка заблокированных видео
- Аналитика и метрики по креативам
- Встроенный Telegram bot UI