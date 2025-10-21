# Исправление ошибок отступов

## ❌ Проблема
```
IndentationError: unexpected indent
File "main.py", line 751
```

## 🔧 Причина
При редактировании кода в функции `process_thumbnail()` были добавлены лишние пробелы в отступах, что привело к некорректной структуре кода.

## ✅ Исправлено

### 1. Блок извлечения первого кадра (строка 751)
**Было:**
```python
            thumbnail_path = thumbnails_dir / f"{uuid.uuid4()}_first_frame.jpg"
            
                   ffmpeg_cmd = [  # ❌ Неправильный отступ
                       'ffmpeg', '-i', video_path,
```

**Стало:**
```python
            thumbnail_path = thumbnails_dir / f"{uuid.uuid4()}_first_frame.jpg"
            
            ffmpeg_cmd = [  # ✅ Правильный отступ
                'ffmpeg', '-i', video_path,
```

### 2. Блок извлечения кадра для модалки (строка 774)
**Было:**
```python
            thumbnail_path = thumbnails_dir / f"{uuid.uuid4()}_with_modal.jpg"
            
                   # Сначала извлекаем первый кадр  # ❌
                   temp_frame = thumbnails_dir / f"temp_frame_{uuid.uuid4()}.jpg"
```

**Стало:**
```python
            thumbnail_path = thumbnails_dir / f"{uuid.uuid4()}_with_modal.jpg"
            
            # Сначала извлекаем первый кадр  # ✅
            temp_frame = thumbnails_dir / f"temp_frame_{uuid.uuid4()}.jpg"
```

### 3. Блок наложения модалки (строка 798)
**Было:**
```python
            modal_path = modal_data["file_path"]
            
                   # Накладываем модалку на кадр  # ❌
                   try:
```

**Стало:**
```python
            modal_path = modal_data["file_path"]
            
            # Накладываем модалку на кадр  # ✅
            try:
```

### 4. Исправлена переменная в error handler (строка 372)
**Было:**
```python
"video_title": f"{campaign_name} {current_date} #{i+1}",  # ❌ current_date не определена
```

**Стало:**
```python
"video_title": f"{campaign_name} Видео #{i+1}",  # ✅
```

## 🧪 Проверка
```bash
# Запуск сервера
cd backend
source venv/bin/activate
python main.py

# ✅ Сервер запустился без ошибок
```

## 📊 Результат
- ✅ Все ошибки отступов исправлены
- ✅ Код соответствует PEP 8
- ✅ Сервер запускается успешно
- ✅ Функциональность не нарушена

**Дата исправления:** 21.10.2025

