# 🔧 Настройка Supabase для UAC Creative Manager

## 📋 Шаги настройки

### 1. Получение API ключей

1. Перейдите в [Supabase Dashboard](https://supabase.com/dashboard)
2. Войдите в ваш проект: `qredhtffydtdxfnokpve`
3. Перейдите в **Settings** → **API**
4. Скопируйте следующие ключи:
   - **anon/public key** - для клиентского приложения
   - **service_role key** - для серверного приложения (держите в секрете!)

### 2. Создание таблиц в базе данных

Выполните SQL скрипт из файла `backend/sql/create_tables.sql`:

1. В Supabase Dashboard перейдите в **SQL Editor**
2. Создайте новый запрос
3. Скопируйте и выполните содержимое файла `backend/sql/create_tables.sql`
4. Проверьте, что все таблицы созданы в разделе **Table Editor**

### 3. Инициализация тестовых данных

Выполните SQL скрипт из файла `backend/sql/init_data.sql`:

1. В **SQL Editor** создайте новый запрос
2. Скопируйте и выполните содержимое файла `backend/sql/init_data.sql`
3. Проверьте данные в **Table Editor**

### 4. Настройка переменных окружения

Создайте файл `.env` в папке `backend/` на основе `config_example.py`:

```bash
cd backend
cp config_example.py config.py
```

Отредактируйте `config.py` и укажите ваши API ключи:

```python
SUPABASE_URL = "https://qredhtffydtdxfnokpve.supabase.co"
SUPABASE_KEY = "ваш_anon_ключ_здесь"
SUPABASE_SERVICE_KEY = "ваш_service_role_ключ_здесь"
```

### 5. Тестирование подключения

Запустите скрипт инициализации:

```bash
cd backend
python3 init_db.py
```

Если все настроено правильно, вы увидите:
```
✅ База данных успешно инициализирована!
✅ Все тесты подключений прошли успешно!
```

## 🔍 Проверка настройки

### Проверка таблиц
В Supabase Dashboard → **Table Editor** должны быть созданы таблицы:
- ✅ `roles` - роли пользователей
- ✅ `users` - пользователи
- ✅ `oauth_credentials` - OAuth учетные данные
- ✅ `modal_images` - изображения модалок
- ✅ `templates` - шаблоны креативов
- ✅ `uploads` - загрузки видео
- ✅ `logs` - логи действий

### Проверка данных
В таблицах должны быть тестовые данные:
- **roles**: admin, user, viewer
- **users**: test@example.com
- **templates**: 3 тестовых шаблона
- **modal_images**: 3 тестовые модалки
- **uploads**: 3 тестовые загрузки

## 🚀 Запуск приложения

После настройки Supabase:

```bash
# Backend
cd backend
python3 main.py

# Frontend (в новом терминале)
cd frontend
npm start
```

## 🐛 Решение проблем

### Ошибка "Invalid API key"
- Проверьте правильность API ключей в `config.py`
- Убедитесь, что используете правильный проект

### Ошибка "Table doesn't exist"
- Выполните SQL скрипт создания таблиц
- Проверьте, что таблицы созданы в Supabase Dashboard

### Ошибка подключения
- Проверьте интернет-соединение
- Убедитесь, что проект Supabase активен
- Проверьте URL проекта

## 📊 Мониторинг

В Supabase Dashboard можно отслеживать:
- **Logs** - все действия пользователей
- **Database** - состояние таблиц
- **API** - использование API ключей
- **Storage** - загруженные файлы

## 🔐 Безопасность

⚠️ **Важно:**
- Никогда не коммитьте `.env` файлы в Git
- Используйте `service_role` ключ только на сервере
- Ограничьте доступ к API ключам
- Регулярно ротируйте ключи

## 📞 Поддержка

При возникновении проблем:
1. Проверьте логи в Supabase Dashboard
2. Убедитесь, что все шаги настройки выполнены
3. Проверьте правильность API ключей
4. Обратитесь к документации Supabase
