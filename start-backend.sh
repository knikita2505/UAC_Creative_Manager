#!/bin/bash

echo "🚀 Запуск UAC Creative Manager Backend..."

# Переход в директорию backend
cd backend

# Проверка наличия Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 не найден. Пожалуйста, установите Python 3.8+"
    exit 1
fi

# Создание виртуального окружения если не существует
if [ ! -d "venv" ]; then
    echo "📦 Создание виртуального окружения..."
    python3 -m venv venv
fi

# Активация виртуального окружения
echo "🔧 Активация виртуального окружения..."
source venv/bin/activate

# Установка зависимостей
echo "📥 Установка зависимостей..."
pip install -r requirements.txt

# Создание необходимых директорий
mkdir -p uploads/videos
mkdir -p uploads/modals
mkdir -p processed
mkdir -p thumbnails
mkdir -p downloaded

# Запуск сервера
echo "🌟 Запуск FastAPI сервера на http://localhost:8000"
python main.py
