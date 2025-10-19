# 📦 Структура базы данных Supabase

Эта структура покрывает все модули платформы:
- Загрузка видео
- Хранение шаблонов
- Пользователи и роли
- Интеграции OAuth
- Работа с кастомными модалками
- Мониторинг и логи

---

## 👤 users

| Поле | Тип | Описание |
|------|-----|----------|
| id | UUID | ID пользователя |
| email | TEXT | Email (уникальный) |
| role_id | UUID | Связь с таблицей roles |
| created_at | TIMESTAMP | Дата регистрации |

---

## 🔐 roles

| Поле | Тип | Описание |
|------|-----|----------|
| id | UUID | Уникальный ID |
| name | TEXT | Имя роли (например, admin, user) |
| description | TEXT | Описание |

---

## 🔑 oauth_credentials

| Поле | Тип | Описание |
|------|-----|----------|
| service | TEXT | youtube / google_ads / telegram |
| client_id / client_secret | TEXT | OAuth-данные |
| access_token / refresh_token | TEXT | Токены |
| token_expires_at | TIMESTAMP | Время жизни токена |

---

## 🎞 modal_images

| Поле | Тип | Описание |
|------|-----|----------|
| image_url | TEXT | Ссылка на изображение модалки |
| is_active | BOOLEAN | Используется ли в данный момент |

---

## 🧱 templates

| Поле | Тип | Описание |
|------|-----|----------|
| lang | TEXT | Язык (en, ru и т.п.) |
| style | TEXT | Стиль (classic, modern) |
| orientation | TEXT | Вертикаль/горизонталь |
| background | TEXT | Цветовая схема |
| ai_tag | TEXT | Модалка / вирус / сабы |
| ai_text | TEXT | Распознанный текст |
| ai_hardness | INT | Агрессивность (1–5) |

---

## 📤 uploads

| Поле | Тип | Описание |
|------|-----|----------|
| youtube_url | TEXT | Ссылка на загруженное видео |
| video_title | TEXT | Название при загрузке |
| thumbnail_type | TEXT | none / first_frame / soft_modal |
| thumbnail_image_id | UUID | если soft_modal — откуда взять изображение |
| status | TEXT | active / banned / pending / error |
| performance | JSONB | метрики GAds: spend, ctr и т.д. |

---

## 🧾 logs

| Поле | Тип | Описание |
|------|-----|----------|
| action | TEXT | Название действия |
| metadata | JSONB | Контекст действия |

---

## 📌 Связи:

- `uploads.template_id → templates.id`
- `uploads.thumbnail_image_id → modal_images.id`
- `oauth_credentials.user_id → users.id`
- `users.role_id → roles.id`
- `logs.user_id → users.id`

---

## Данные проекта Supabase

- Project ID: qredhtffydtdxfnokpve
- host: db.qredhtffydtdxfnokpve.supabase.co
- port: 5432
- database: postgres
- user: postgres
- direct connection uri: postgresql://postgres:privet*anDreI798!@db.qredhtffydtdxfnokpve.supabase.co:5432/postgres

---

## ⛳ Примечания:

- В будущем можно расширить шаблоны и загрузки до новых версий.
- Таблица `modal_images` позволяет безопасно генерировать кастомные превью.
