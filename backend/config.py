import os
from dotenv import load_dotenv

# Загрузка переменных окружения
load_dotenv()

# Supabase настройки
SUPABASE_URL = "https://qredhtffydtdxfnokpve.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InFyZWRodGZmeWR0ZHhmbm9rcHZlIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjA3MzYxNzAsImV4cCI6MjA3NjMxMjE3MH0.jbfFPZcv1_0jRrl9eU68-mf6a4witvM5BzwOy1eStrQ"  # Получите в Supabase Dashboard > Settings > API
SUPABASE_SERVICE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InFyZWRodGZmeWR0ZHhmbm9rcHZlIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2MDczNjE3MCwiZXhwIjoyMDc2MzEyMTcwfQ.PghMbqpdXqAc4qIurroLYnPB-jMHOq01xEfll97AM44"  # Получите в Supabase Dashboard > Settings > API

# PostgreSQL настройки (прямое подключение)
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:privet*anDreI798!@db.qredhtffydtdxfnokpve.supabase.co:5432/postgres")

# Настройки приложения
DEBUG = os.getenv("DEBUG", "True").lower() == "true"
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-here")

# CORS настройки
ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:8000",
    "http://127.0.0.1:8000",
]

# Настройки файлов
UPLOAD_DIR = "uploads"
MAX_FILE_SIZE = 100 * 1024 * 1024  # 100MB
ALLOWED_VIDEO_TYPES = ["video/mp4", "video/avi", "video/mov", "video/mkv", "video/webm"]
ALLOWED_IMAGE_TYPES = ["image/jpeg", "image/png", "image/gif", "image/webp"]
