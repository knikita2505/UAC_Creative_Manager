# 🔗 Руководство по интеграциям UAC Creative Manager

## 📋 Обзор

Платформа поддерживает интеграции с внешними сервисами для автоматизации работы с видео-креативами:

- **YouTube Data API** - загрузка видео
- **Telegram Bot API** - уведомления
- **Google Drive API** - скачивание файлов
- **Google Ads API** - управление кампаниями

## 🎯 DoD (Definition of Done) - Выполнено ✅

- ✅ **Данные сохраняются в БД** - все настройки интеграций сохраняются в таблице `oauth_credentials`
- ✅ **Реальное тестирование подключений** - каждый сервис тестируется через реальные API
- ✅ **Интеграции настроены** - полная настройка через веб-интерфейс
- ✅ **Обработка ошибок** - подробное логирование и обработка ошибок

---

## 🎥 YouTube Data API

### Настройка

1. **Создание проекта в Google Cloud Console**
   - Перейдите в [Google Cloud Console](https://console.cloud.google.com/)
   - Создайте новый проект или выберите существующий
   - Включите YouTube Data API v3

2. **Создание OAuth2 credentials**
   - Перейдите в "Credentials" → "Create Credentials" → "OAuth client ID"
   - Выберите "Web application"
   - Добавьте redirect URI: `http://localhost:8000/auth/youtube/callback`

3. **Настройка в платформе**
   - Перейдите в раздел "Настройки" → "OAuth"
   - Введите Client ID и Client Secret
   - Нажмите "Сохранить"

### Функции

- **Загрузка видео** - автоматическая загрузка на YouTube
- **Управление метаданными** - настройка названия, описания, тегов
- **Обработка миниатюр** - наложение кастомных миниатюр

### API Endpoints

```bash
# Настройка YouTube
POST /integrations/youtube/setup
Content-Type: application/x-www-form-urlencoded

client_id=YOUR_CLIENT_ID
client_secret=YOUR_CLIENT_SECRET
redirect_uri=http://localhost:8000/auth/youtube/callback

# Тестирование подключения
POST /integrations/youtube/test

# Загрузка видео
POST /upload/video
```

---

## 📱 Telegram Bot API

### Настройка

1. **Создание бота**
   - Найдите [@BotFather](https://t.me/botfather) в Telegram
   - Отправьте команду `/newbot`
   - Следуйте инструкциям для создания бота
   - Получите токен бота

2. **Получение Chat ID (опционально)**
   - Найдите [@userinfobot](https://t.me/userinfobot)
   - Отправьте любое сообщение
   - Скопируйте ваш Chat ID

3. **Настройка в платформе**
   - Перейдите в раздел "Настройки" → "Telegram"
   - Введите Bot Token
   - Введите Chat ID (для уведомлений)
   - Нажмите "Сохранить"

### Функции

- **Уведомления о загрузках** - автоматические уведомления о статусе
- **Уведомления о банах** - оповещения о заблокированных креативах
- **Тестовые сообщения** - проверка работы бота

### API Endpoints

```bash
# Настройка Telegram Bot
POST /integrations/telegram/setup
Content-Type: application/x-www-form-urlencoded

bot_token=YOUR_BOT_TOKEN
chat_id=YOUR_CHAT_ID

# Тестирование подключения
POST /integrations/telegram/test

# Отправка уведомления
POST /integrations/telegram/send-notification
Content-Type: application/x-www-form-urlencoded

message=Test notification
```

---

## 💾 Google Drive API

### Настройка

1. **Включение Google Drive API**
   - В том же проекте Google Cloud Console
   - Включите Google Drive API
   - Создайте OAuth2 credentials (отдельные от YouTube)

2. **Настройка в платформе**
   - Перейдите в раздел "Настройки" → "OAuth"
   - Найдите секцию "Google Drive API"
   - Введите Client ID и Client Secret
   - Нажмите "Сохранить"

### Функции

- **Скачивание видео** - загрузка видео из Google Drive
- **Обработка ссылок** - автоматическое извлечение file_id из ссылок
- **Проверка доступа** - валидация прав доступа к файлам

### API Endpoints

```bash
# Настройка Google Drive
POST /integrations/google-drive/setup
Content-Type: application/x-www-form-urlencoded

client_id=YOUR_CLIENT_ID
client_secret=YOUR_CLIENT_SECRET
redirect_uri=http://localhost:8000/auth/drive/callback

# Тестирование подключения
POST /integrations/google-drive/test
```

---

## 📊 Google Ads API

### Настройка

1. **Получение Developer Token**
   - Перейдите в [Google Ads API Center](https://ads.google.com/aw/apicenter)
   - Подайте заявку на получение Developer Token
   - Дождитесь одобрения (может занять несколько дней)

2. **Настройка OAuth2 для Google Ads**
   - Используйте отдельный проект Google Cloud Console
   - Включите Google Ads API
   - Создайте OAuth2 credentials

3. **Получение Refresh Token**
   - Используйте OAuth2 Playground для получения refresh token
   - Настройте redirect URI: `https://developers.google.com/oauthplayground`

4. **Настройка в платформе**
   - Перейдите в раздел "Настройки" → "OAuth"
   - Найдите секцию "Google Ads API"
   - Заполните все поля (Client ID, Client Secret, Refresh Token, Developer Token, Customer ID)
   - Нажмите "Сохранить"

### Функции

- **Мониторинг кампаний** - отслеживание статуса креативов
- **Получение метрик** - статистика по кампаниям
- **Управление креативами** - автоматическое добавление в кампании

### API Endpoints

```bash
# Настройка Google Ads
POST /integrations/google-ads/setup
Content-Type: application/x-www-form-urlencoded

client_id=YOUR_CLIENT_ID
client_secret=YOUR_CLIENT_SECRET
refresh_token=YOUR_REFRESH_TOKEN
developer_token=YOUR_DEVELOPER_TOKEN
customer_id=YOUR_CUSTOMER_ID

# Тестирование подключения
POST /integrations/google-ads/test
```

---

## 🔍 Статус интеграций

### Проверка статуса

```bash
# Получение статуса всех интеграций
GET /integrations/status
```

Ответ:
```json
{
  "integrations": {
    "youtube": {
      "configured": true,
      "has_credentials": true,
      "authorized": true
    },
    "telegram": {
      "configured": true,
      "has_credentials": true
    },
    "google_drive": {
      "configured": true,
      "has_credentials": true,
      "authorized": false
    },
    "google_ads": {
      "configured": true,
      "has_credentials": true,
      "authorized": true
    }
  }
}
```

### Статусы

- **configured** - настройки сохранены в БД
- **has_credentials** - есть необходимые учетные данные
- **authorized** - выполнена авторизация (для OAuth2 сервисов)

---

## 🔧 Техническая реализация

### Архитектура

```
Frontend (React) → Backend (FastAPI) → Integrations Manager → External APIs
                                      ↓
                                  Supabase DB
```

### Компоненты

1. **IntegrationManager** - основной класс для управления интеграциями
2. **DatabaseManager** - сохранение настроек в БД
3. **API Endpoints** - REST API для настройки и тестирования
4. **Frontend Components** - веб-интерфейс для управления

### Безопасность

- **Шифрование токенов** - все токены сохраняются в зашифрованном виде
- **Валидация данных** - проверка всех входящих данных
- **Логирование** - все действия записываются в логи
- **Обработка ошибок** - корректная обработка всех ошибок

---

## 🚀 Быстрый старт

### 1. Настройка YouTube

```bash
# 1. Получите OAuth2 credentials в Google Cloud Console
# 2. В веб-интерфейсе:
#    - Перейдите в "Настройки" → "OAuth"
#    - Заполните YouTube Client ID и Secret
#    - Нажмите "Сохранить"
# 3. Перейдите по ссылке авторизации
# 4. Нажмите "Тестировать" для проверки
```

### 2. Настройка Telegram

```bash
# 1. Создайте бота через @BotFather
# 2. В веб-интерфейсе:
#    - Перейдите в "Настройки" → "Telegram"
#    - Введите Bot Token
#    - Нажмите "Сохранить"
# 3. Нажмите "Тестировать" для проверки
```

### 3. Проверка статуса

```bash
# В веб-интерфейсе перейдите в "Настройки"
# Статус интеграций отображается с иконками:
# ✅ - настроено и работает
# ⚠️ - настроено, но не авторизовано
# ❌ - не настроено
```

---

## 🐛 Решение проблем

### Частые ошибки

1. **"Invalid API key"**
   - Проверьте правильность API ключей
   - Убедитесь, что используете правильный проект

2. **"Unauthorized"**
   - Выполните авторизацию через OAuth2
   - Проверьте права доступа к API

3. **"Rate limit exceeded"**
   - Подождите некоторое время
   - Проверьте лимиты в консоли разработчика

4. **"Connection timeout"**
   - Проверьте интернет-соединение
   - Убедитесь, что API сервис доступен

### Логи

Все действия логируются в таблицу `logs`:
```sql
SELECT * FROM logs WHERE action LIKE '%integration%' ORDER BY created_at DESC;
```

---

## 📞 Поддержка

При возникновении проблем:

1. Проверьте логи в Supabase Dashboard
2. Убедитесь, что все API ключи корректны
3. Проверьте статус интеграций через `/integrations/status`
4. Обратитесь к документации конкретных API
5. Создайте issue в репозитории проекта

---

## 🎉 Заключение

Все интеграции настроены и готовы к использованию! Система автоматически:

- Сохраняет настройки в БД
- Тестирует подключения
- Обрабатывает ошибки
- Логирует все действия

Теперь вы можете полноценно использовать все функции платформы для автоматизации работы с видео-креативами.
