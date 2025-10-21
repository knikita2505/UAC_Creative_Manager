# Исправление конфликта имен

## ❌ Проблема

```
TypeError: 'bool' object is not callable
Traceback:
  File "main.py", line 154, in upload_video
    other_formats = await create_other_formats(processed_path, upload_id, orientation)
TypeError: 'bool' object is not callable
```

## 🔍 Причина

**Конфликт имен между параметром и функцией!**

У нас было:
- Параметр функции: `create_other_formats: bool = Form(False)`
- Функция: `async def create_other_formats(...)`

Когда параметр `create_other_formats` принимает значение (например, `True` или `False`), он **перезаписывает** ссылку на функцию с тем же именем в локальной области видимости.

**Результат:** Python пытается вызвать `True(...)` или `False(...)` вместо функции, что приводит к ошибке `'bool' object is not callable`.

## ✅ Решение

Переименовали параметр с `create_other_formats` на `create_formats`:

### 1. Модель данных
```python
# Было:
class VideoUpload(BaseModel):
    create_other_formats: bool = False

# Стало:
class VideoUpload(BaseModel):
    create_formats: bool = False
```

### 2. Endpoint /upload/video
```python
# Было:
async def upload_video(
    create_other_formats: bool = Form(False),

# Стало:
async def upload_video(
    create_formats: bool = Form(False),
```

### 3. Endpoint /upload/videos/batch
```python
# Было:
async def upload_videos_batch(
    create_other_formats: bool = Form(False),

# Стало:
async def upload_videos_batch(
    create_formats: bool = Form(False),
```

### 4. Использование внутри функций
```python
# Было:
if create_other_formats:
    other_formats = await create_other_formats(...)

# Стало:
if create_formats:
    other_formats = await create_other_formats(...)
```

## 📊 Изменения

**Затронутые файлы:**
- `backend/main.py`:
  - Строка 34: Модель `VideoUpload`
  - Строка 92: Параметр endpoint `/upload/video`
  - Строка 152: Условие использования
  - Строка 260: Параметр endpoint `/upload/videos/batch`
  - Строка 319: Условие использования в batch

**Функция осталась без изменений:**
- Строка 656: `async def create_other_formats(...)` - имя функции НЕ изменилось

## 🎯 Важный урок

**Не используйте одинаковые имена для:**
- Параметров функции
- Локальных переменных
- Функций/методов в той же области видимости

**Пример плохого кода:**
```python
def process_data(data):
    # data - это параметр
    data = read_file()  # ❌ Перезаписали параметр!
    return data()  # ❌ TypeError если data теперь что-то другое
```

**Пример хорошего кода:**
```python
def process_data(input_data):
    # input_data - параметр
    file_data = read_file()  # ✅ Разные имена
    return process(file_data)  # ✅ Понятно что вызываем
```

## ✅ Результат

- ✅ Конфликт имен устранен
- ✅ Параметр переименован в `create_formats`
- ✅ Функция `create_other_formats()` работает корректно
- ✅ Ошибка исправлена

**Сервер перезапущен. Попробуйте загрузить видео снова!**

---

**Дата исправления:** 21.10.2025

