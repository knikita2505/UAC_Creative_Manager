# 🔧 Инструкции по установке UAC Creative Manager

## 📋 Предварительные требования

### 1. Python 3.8+
```bash
# Проверка версии Python
python3 --version

# Если Python не установлен, установите через Homebrew:
brew install python3
```

### 2. Node.js 16+ и npm
```bash
# Проверка версии Node.js
node --version
npm --version

# Если Node.js не установлен, установите через Homebrew:
brew install node

# Или скачайте с официального сайта:
# https://nodejs.org/
```

### 3. Git
```bash
# Проверка версии Git
git --version

# Если Git не установлен:
brew install git
```

## 🚀 Установка проекта

### 1. Клонирование репозитория
```bash
git clone <repository-url>
cd UAC_Creative_Manager
```

### 2. Установка Backend зависимостей
```bash
cd backend
python3 -m pip install -r requirements.txt
```

### 3. Установка Frontend зависимостей
```bash
cd ../frontend
npm install
```

## 🎯 Запуск проекта

### Вариант 1: Автоматический запуск
```bash
# Backend (в первом терминале)
./start-backend.sh

# Frontend (во втором терминале)
./start-frontend.sh
```

### Вариант 2: Ручной запуск

#### Backend:
```bash
cd backend
python3 main.py
```
Backend будет доступен по адресу: http://localhost:8000

#### Frontend:
```bash
cd frontend
npm start
```
Frontend будет доступен по адресу: http://localhost:3000

## 🔍 Проверка работы

### Backend API
```bash
curl http://localhost:8000/
# Должен вернуть: {"message":"UAC Creative Manager API"}
```

### API Документация
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### Frontend
Откройте браузер и перейдите на: http://localhost:3000

## 🐛 Решение проблем

### Ошибка "command not found: python3"
```bash
# Установите Python через Homebrew
brew install python3

# Или используйте python вместо python3
python --version
```

### Ошибка "command not found: npm"
```bash
# Установите Node.js через Homebrew
brew install node

# Или скачайте с официального сайта
# https://nodejs.org/
```

### Ошибка "Permission denied" при запуске скриптов
```bash
chmod +x start-backend.sh
chmod +x start-frontend.sh
```

### Порт уже используется
```bash
# Найдите процесс, использующий порт 8000
lsof -i :8000

# Убейте процесс
kill -9 <PID>

# Или измените порт в коде
```

## 📦 Дополнительные зависимости (опционально)

### Для обработки видео:
```bash
# FFmpeg (для обработки видео)
brew install ffmpeg

# OpenCV (для работы с изображениями)
pip3 install opencv-python
```

### Для Google API интеграций:
```bash
# После настройки OAuth2, раскомментируйте в requirements.txt:
# google-auth
# google-auth-oauthlib
# google-api-python-client
```

## 🎨 Структура проекта

```
UAC_Creative_Manager/
├── backend/                 # FastAPI backend
│   ├── main.py             # Основной файл API
│   ├── requirements.txt    # Python зависимости
│   └── Dockerfile          # Docker контейнер
├── frontend/               # React frontend
│   ├── src/
│   │   ├── components/    # React компоненты
│   │   ├── App.js         # Главный компонент
│   │   └── index.js       # Точка входа
│   ├── package.json       # Node.js зависимости
│   └── Dockerfile         # Docker контейнер
├── docker-compose.yml      # Docker Compose
├── start-backend.sh        # Скрипт запуска backend
├── start-frontend.sh       # Скрипт запуска frontend
└── README.md              # Основная документация
```

## 🔧 Настройка переменных окружения

Создайте файл `.env` в корне проекта на основе `env.example`:

```bash
cp env.example .env
# Отредактируйте .env файл с вашими настройками
```

## 📱 Использование

1. **Загрузка модалок**: Раздел "Модалки" → загрузите изображения
2. **Загрузка видео**: Раздел "Загрузка видео" → выберите файл и настройки
3. **Просмотр реестра**: Раздел "Реестр креативов" → все загрузки
4. **Настройки**: Раздел "Настройки" → конфигурация интеграций

## 🆘 Получение помощи

Если у вас возникли проблемы:
1. Проверьте все предварительные требования
2. Убедитесь, что все зависимости установлены
3. Проверьте логи в консоли
4. Создайте issue в репозитории проекта
