from fastapi import FastAPI, HTTPException, UploadFile, File, Form, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Optional
import os
import uuid
from datetime import datetime
import asyncio
import aiofiles
from pathlib import Path

app = FastAPI(title="UAC Creative Manager", version="1.0.0")

# CORS настройки
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Модели данных
class VideoUpload(BaseModel):
    campaign_name: str
    video_source: str  # "local" или "drive_url"
    drive_url: Optional[str] = None
    thumbnail_option: str  # "none", "first_frame", "custom_modal"
    modal_image_id: Optional[str] = None

class Template(BaseModel):
    id: str
    language: str
    style: str
    background: str
    aggressiveness: str
    category: str
    characteristics: List[str]
    created_at: datetime

class Upload(BaseModel):
    id: str
    template_id: Optional[str]
    youtube_url: str
    campaign_name: str
    upload_date: datetime
    status: str  # "active", "banned"
    ad_group: Optional[str] = None
    metrics: Optional[dict] = None

# Временное хранение в памяти (позже заменим на Supabase)
templates_db = []
uploads_db = []
modal_images_db = []

@app.get("/")
async def root():
    return {"message": "UAC Creative Manager API"}

@app.post("/upload/video")
async def upload_video(
    campaign_name: str = Form(...),
    video_source: str = Form(...),
    drive_url: Optional[str] = Form(None),
    thumbnail_option: str = Form(...),
    modal_image_id: Optional[str] = Form(None),
    video_file: Optional[UploadFile] = File(None)
):
    """Загрузка видео на YouTube"""
    try:
        # Генерация уникального ID для загрузки
        upload_id = str(uuid.uuid4())
        
        # Создание названия видео: название кампании + дата
        current_date = datetime.now().strftime("%d-%m-%y")
        video_title = f"{campaign_name} {current_date}"
        
        # Обработка видео в зависимости от источника
        if video_source == "local" and video_file:
            # Обработка локального файла
            file_path = await save_uploaded_file(video_file)
            processed_path = await process_video(file_path, upload_id)
        elif video_source == "drive" and drive_url:
            # Скачивание из Google Drive
            processed_path = await download_from_drive(drive_url, upload_id)
        else:
            raise HTTPException(status_code=400, detail="Неверные параметры загрузки")
        
        # Обработка миниатюры
        thumbnail_path = await process_thumbnail(
            processed_path, thumbnail_option, modal_image_id
        )
        
        # Загрузка на YouTube (заглушка)
        youtube_url = await upload_to_youtube(processed_path, video_title, thumbnail_path)
        
        # Сохранение в реестр
        upload_record = Upload(
            id=upload_id,
            template_id=None,
            youtube_url=youtube_url,
            campaign_name=campaign_name,
            upload_date=datetime.now(),
            status="active"
        )
        uploads_db.append(upload_record)
        
        return {
            "success": True,
            "upload_id": upload_id,
            "youtube_url": youtube_url,
            "video_title": video_title
        }
        
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"success": False, "error": str(e)}
        )

@app.post("/upload/modal")
async def upload_modal_image(image: UploadFile = File(...)):
    """Загрузка изображения модалки для наложения на кадры"""
    try:
        modal_id = str(uuid.uuid4())
        
        # Сохранение изображения
        upload_dir = Path("uploads/modals")
        upload_dir.mkdir(parents=True, exist_ok=True)
        
        file_path = upload_dir / f"{modal_id}_{image.filename}"
        async with aiofiles.open(file_path, 'wb') as f:
            content = await image.read()
            await f.write(content)
        
        # Сохранение метаданных
        modal_data = {
            "id": modal_id,
            "filename": image.filename,
            "file_path": str(file_path),
            "upload_date": datetime.now()
        }
        modal_images_db.append(modal_data)
        
        return {
            "success": True,
            "modal_id": modal_id,
            "filename": image.filename
        }
        
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"success": False, "error": str(e)}
        )

@app.get("/modals")
async def get_modal_images():
    """Получение списка загруженных модалок"""
    return {
        "modals": [
            {
                "id": modal["id"],
                "filename": modal["filename"],
                "upload_date": modal["upload_date"]
            }
            for modal in modal_images_db
        ]
    }

@app.get("/uploads")
async def get_uploads():
    """Получение списка загрузок"""
    return {"uploads": uploads_db}

@app.get("/templates")
async def get_templates():
    """Получение списка шаблонов"""
    return {"templates": templates_db}

# Вспомогательные функции
async def save_uploaded_file(file: UploadFile) -> str:
    """Сохранение загруженного файла"""
    upload_dir = Path("uploads/videos")
    upload_dir.mkdir(parents=True, exist_ok=True)
    
    file_path = upload_dir / f"{uuid.uuid4()}_{file.filename}"
    async with aiofiles.open(file_path, 'wb') as f:
        content = await file.read()
        await f.write(content)
    
    return str(file_path)

async def process_video(file_path: str, upload_id: str) -> str:
    """Обработка видео: очистка метаданных и уникализация"""
    # Здесь будет логика очистки метаданных через exiftool/ffmpeg
    # и легкая уникализация (изменение длительности, битрейта, FPS)
    processed_path = f"processed/{upload_id}_processed.mp4"
    
    # Заглушка - простое копирование
    import shutil
    shutil.copy2(file_path, processed_path)
    
    return processed_path

async def download_from_drive(drive_url: str, upload_id: str) -> str:
    """Скачивание видео из Google Drive"""
    # Здесь будет логика скачивания из Google Drive
    # Пока заглушка
    return f"downloaded/{upload_id}_from_drive.mp4"

async def process_thumbnail(video_path: str, option: str, modal_id: Optional[str]) -> Optional[str]:
    """Обработка миниатюры"""
    if option == "none":
        return None
    elif option == "first_frame":
        # Извлечение первого кадра
        return f"thumbnails/{uuid.uuid4()}_first_frame.jpg"
    elif option == "custom_modal" and modal_id:
        # Наложение модалки на первый кадр
        return f"thumbnails/{uuid.uuid4()}_with_modal.jpg"
    
    return None

async def upload_to_youtube(video_path: str, title: str, thumbnail_path: Optional[str]) -> str:
    """Загрузка видео на YouTube"""
    # TODO: Здесь будет интеграция с YouTube Data API
    # Пока возвращаем заглушку для демонстрации
    import time
    await asyncio.sleep(1)  # Имитация загрузки
    return f"https://youtube.com/watch?v={str(uuid.uuid4())[:11]}"

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
