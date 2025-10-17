#!/bin/bash

echo "🚀 Запуск UAC Creative Manager Frontend..."

# Переход в директорию frontend
cd frontend

# Проверка наличия Node.js
if ! command -v node &> /dev/null; then
    echo "❌ Node.js не найден. Пожалуйста, установите Node.js 16+"
    exit 1
fi

# Проверка наличия npm
if ! command -v npm &> /dev/null; then
    echo "❌ npm не найден. Пожалуйста, установите npm"
    exit 1
fi

# Установка зависимостей
echo "📥 Установка зависимостей..."
npm install

# Запуск React приложения
echo "🌟 Запуск React приложения на http://localhost:3000"
npm start
