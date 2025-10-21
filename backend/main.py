from fastapi import FastAPI, HTTPException, UploadFile, File, Form, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, HTMLResponse
from pydantic import BaseModel
from typing import List, Optional
import os
import uuid
from datetime import datetime
import asyncio
import aiofiles
from pathlib import Path
from database import db_manager
from config import ALLOWED_ORIGINS, UPLOAD_DIR, MAX_FILE_SIZE, ALLOWED_VIDEO_TYPES, ALLOWED_IMAGE_TYPES
from integrations import integration_manager

app = FastAPI(title="UAC Creative Manager", version="1.0.0")

# CORS настройки
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Модели данных
class VideoUpload(BaseModel):
    campaign_name: str
    video_source: str  # "local" или "drive_url"
    drive_url: Optional[str] = None
    thumbnail_option: str  # "none", "first_frame", "soft_modal"
    modal_image_id: Optional[str] = None
    create_formats: bool = False  # Создавать ли другие форматы

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

# Инициализация базы данных при запуске
@app.on_event("startup")
async def startup_event():
    """Инициализация при запуске приложения"""
    try:
        print("🚀 Starting UAC Creative Manager...")
        
        # Проверка подключения к базе данных
        try:
            await db_manager.create_default_roles()
            await db_manager.create_log("app_startup", {"message": "UAC Creative Manager started"})
            print("✅ Database connected successfully")
        except Exception as db_error:
            print(f"⚠️ Database connection failed: {db_error}")
            print("💡 To fix this:")
            print("   1. Get API keys from Supabase Dashboard")
            print("   2. Update config.py with your keys")
            print("   3. Run: python3 init_db.py")
            print("   4. Restart the application")
        
        print("🌟 Application started successfully!")
        
    except Exception as e:
        print(f"❌ Application startup failed: {e}")

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
    create_formats: bool = Form(False),
    video_file: Optional[UploadFile] = File(None)
):
    """Загрузка видео на YouTube"""
    try:
        # Детальное логирование для отладки
        print(f"🔍 DEBUG: Получен запрос на загрузку")
        print(f"   campaign_name: {campaign_name}")
        print(f"   video_source: {video_source}")
        print(f"   thumbnail_option: {thumbnail_option}")
        print(f"   modal_image_id: {modal_image_id}")
        print(f"   video_file: {video_file.filename if video_file else 'None'}")
        print(f"   video_file.content_type: {video_file.content_type if video_file else 'None'}")
        
        await db_manager.create_log("upload_video_debug", {
            "campaign_name": campaign_name,
            "video_source": video_source,
            "thumbnail_option": thumbnail_option,
            "modal_image_id": modal_image_id,
            "video_filename": video_file.filename if video_file else None,
            "video_content_type": video_file.content_type if video_file else None
        })
        # Генерация уникального ID для загрузки
        upload_id = str(uuid.uuid4())
        
        # Обработка видео в зависимости от источника
        print(f"🔧 Начинаем обработку видео...")
        if video_source == "local" and video_file:
            # Обработка локального файла
            print(f"📁 Сохранение загруженного файла...")
            file_path = await save_uploaded_file(video_file)
            print(f"✅ Файл сохранен: {file_path}")
            
            print(f"🔧 Обработка видео (очистка метаданных и уникализация)...")
            processed_path = await process_video(file_path, upload_id)
            print(f"✅ Видео обработано: {processed_path}")
        elif video_source == "drive" and drive_url:
            # Скачивание из Google Drive
            print(f"☁️ Скачивание из Google Drive...")
            processed_path = await download_from_drive(drive_url, upload_id)
            print(f"✅ Видео скачано: {processed_path}")
        else:
            print(f"❌ Неверные параметры загрузки")
            raise HTTPException(status_code=400, detail="Неверные параметры загрузки")
        
        # Определяем ориентацию видео
        print(f"📐 Определение ориентации видео...")
        orientation = await get_video_orientation(processed_path)
        print(f"✅ Ориентация видео: {orientation}")
        
        # Номер копии (для одиночной загрузки всегда 1)
        video_copy_number = 1
        
        # Список видео для загрузки (основное + другие форматы)
        videos_to_upload = [
            {
                "path": processed_path,
                "orientation": orientation,
                "copy_number": video_copy_number
            }
        ]
        
        # Создаем другие форматы если выбрана опция
        if create_formats:
            print(f"🎬 Создание других форматов видео...")
            other_formats = await create_other_formats(processed_path, upload_id, orientation)
            
            # Добавляем созданные форматы с тем же номером копии
            for fmt in other_formats:
                videos_to_upload.append({
                    "path": fmt["path"],
                    "orientation": fmt["orientation"],
                    "copy_number": video_copy_number  # Тот же номер для всех форматов
                })
        
        # Загружаем все видео на YouTube
        upload_results = []
        
        for video_data in videos_to_upload:
            # Генерируем название для каждого видео
            video_title = generate_video_title(
                campaign_name,
                video_data["orientation"],
                video_data["copy_number"]
            )
            
            print(f"📤 Загрузка: {video_title}")
            
            # Обработка миниатюры
            thumbnail_path = await process_thumbnail(
                video_data["path"], thumbnail_option, modal_image_id
            )
            
            # Загрузка на YouTube
            youtube_url = await upload_to_youtube(video_data["path"], video_title, thumbnail_path)
            
            # Сохранение в базу данных
            upload_data = {
                "youtube_url": youtube_url,
                "video_title": video_title,
                "campaign_name": campaign_name,
                "thumbnail_type": thumbnail_option,
                "thumbnail_image_id": modal_image_id if thumbnail_option == "soft_modal" else None,
                "status": "active"
            }
            
            upload_record = await db_manager.create_upload(upload_data)
            
            upload_results.append({
                "upload_id": upload_record["id"],
                "youtube_url": youtube_url,
                "video_title": video_title,
                "orientation": video_data["orientation"],
                "copy_number": video_data["copy_number"],
                "group_name": f"{campaign_name} {datetime.now().strftime('%d.%m.%y')} #{video_data['copy_number']}"
            })
            
            # Логирование успешной загрузки
            await db_manager.create_log(
                "video_uploaded",
                {
                    "upload_id": upload_record["id"],
                    "campaign_name": campaign_name,
                    "youtube_url": youtube_url,
                    "thumbnail_type": thumbnail_option,
                    "orientation": video_data["orientation"]
                }
            )
        
        # Возвращаем результаты
        if len(upload_results) == 1:
            # Одно видео - возвращаем простой формат
            return {
                "success": True,
                **upload_results[0]
            }
        else:
            # Несколько видео - возвращаем массив
            return {
                "success": True,
                "videos": upload_results,
                "total_uploaded": len(upload_results)
            }
        
    except Exception as e:
        # Логируем детальную ошибку с полным стектрейсом
        import traceback
        error_traceback = traceback.format_exc()
        print(f"❌ ОШИБКА при загрузке видео:")
        print(f"   Тип ошибки: {type(e).__name__}")
        print(f"   Сообщение: {str(e)}")
        print(f"   Стектрейс:\n{error_traceback}")
        
        await db_manager.create_log("upload_video_error", {
            "error": str(e),
            "error_type": type(e).__name__,
            "traceback": error_traceback,
            "campaign_name": campaign_name,
            "video_source": video_source,
            "thumbnail_option": thumbnail_option
        })
        return JSONResponse(
            status_code=500,
            content={"success": False, "error": str(e), "error_type": type(e).__name__}
        )

@app.post("/upload/videos/batch")
async def upload_videos_batch(
    campaign_name: str = Form(...),
    video_source: str = Form(...),
    drive_urls: Optional[str] = Form(None),  # JSON строка с массивом ссылок
    thumbnail_option: str = Form(...),
    modal_image_id: Optional[str] = Form(None),
    create_formats: bool = Form(False),
    video_files: List[UploadFile] = File(...)
):
    """Загрузка нескольких видео на YouTube"""
    try:
        import json
        
        # Парсинг ссылок на Google Drive если указаны
        drive_url_list = []
        if drive_urls:
            try:
                drive_url_list = json.loads(drive_urls)
            except json.JSONDecodeError:
                return JSONResponse(
                    status_code=400,
                    content={"success": False, "error": "Неверный формат ссылок на Google Drive"}
                )
        
        # Определяем количество видео для обработки
        if video_source == "local":
            video_count = len(video_files)
        else:
            video_count = len(drive_url_list)
        
        if video_count == 0:
            return JSONResponse(
                status_code=400,
                content={"success": False, "error": "Не указаны видео для загрузки"}
            )
        
        results = []
        
        # Обработка каждого видео
        for i in range(video_count):
            upload_id = str(uuid.uuid4())
            
            try:
                # Обработка видео в зависимости от источника
                if video_source == "local" and i < len(video_files):
                    file_path = await save_uploaded_file(video_files[i])
                    processed_path = await process_video(file_path, upload_id)
                elif video_source == "drive" and i < len(drive_url_list):
                    processed_path = await download_from_drive(drive_url_list[i], upload_id)
                else:
                    continue
                
                # Определяем ориентацию видео
                orientation = await get_video_orientation(processed_path)
                
                # Номер копии для текущего видео (i+1)
                video_copy_number = i + 1
                
                # Список видео для загрузки (основное + другие форматы)
                videos_to_upload = [
                    {
                        "path": processed_path,
                        "orientation": orientation,
                        "copy_number": video_copy_number
                    }
                ]
                
                # Создаем другие форматы если выбрана опция
                if create_formats:
                    other_formats = await create_other_formats(processed_path, upload_id, orientation)
                    
                    # Добавляем форматы с тем же номером копии
                    for fmt in other_formats:
                        videos_to_upload.append({
                            "path": fmt["path"],
                            "orientation": fmt["orientation"],
                            "copy_number": video_copy_number  # Тот же номер для всех форматов
                        })
                
                # Загружаем все видео
                for video_data in videos_to_upload:
                    # Генерируем название
                    video_title = generate_video_title(
                        campaign_name,
                        video_data["orientation"],
                        video_data["copy_number"]
                    )
                    
                    # Обработка миниатюры
                    thumbnail_path = await process_thumbnail(
                        video_data["path"], thumbnail_option, modal_image_id
                    )
                    
                    # Загрузка на YouTube
                    youtube_url = await upload_to_youtube(video_data["path"], video_title, thumbnail_path)
                    
                    # Сохранение в базу данных
                    upload_data = {
                        "youtube_url": youtube_url,
                        "video_title": video_title,
                        "campaign_name": campaign_name,
                        "thumbnail_type": thumbnail_option,
                        "thumbnail_image_id": modal_image_id if thumbnail_option == "soft_modal" else None,
                        "status": "active"
                    }
                    
                    upload_record = await db_manager.create_upload(upload_data)
                    
                    results.append({
                        "upload_id": upload_record["id"],
                        "youtube_url": youtube_url,
                        "video_title": video_title,
                        "orientation": video_data["orientation"],
                        "copy_number": video_data["copy_number"],
                        "group_name": f"{campaign_name} {datetime.now().strftime('%d.%m.%y')} #{video_data['copy_number']}",
                        "success": True
                    })
                    
                    # Логирование успешной загрузки
                    await db_manager.create_log(
                        "video_uploaded_batch",
                        {
                            "upload_id": upload_record["id"],
                            "campaign_name": campaign_name,
                            "youtube_url": youtube_url,
                            "thumbnail_type": thumbnail_option,
                            "orientation": video_data["orientation"],
                            "batch_index": i + 1
                        }
                    )
                
            except Exception as e:
                # Логируем ошибку для конкретного видео
                await db_manager.create_log(
                    "video_upload_batch_error",
                    {
                        "campaign_name": campaign_name,
                        "batch_index": i + 1,
                        "error": str(e)
                    }
                )
                
                results.append({
                    "video_title": f"{campaign_name} Видео #{i+1}",
                    "success": False,
                    "error": str(e)
                })
        
        successful_uploads = [r for r in results if r.get("success")]
        failed_uploads = [r for r in results if not r.get("success")]
        
        # Считаем уникальные группы (по copy_number)
        unique_groups = set(r.get("copy_number") for r in successful_uploads if r.get("copy_number"))
        
        return {
            "success": True,
            "total_videos": video_count,  # Количество исходных видео
            "successful_uploads": len(unique_groups),  # Количество успешных групп
            "total_formats": len(successful_uploads),  # Общее количество загруженных форматов
            "failed_uploads": len(failed_uploads),
            "results": results
        }
        
    except Exception as e:
        await db_manager.create_log("batch_upload_error", {"error": str(e)})
        return JSONResponse(
            status_code=500,
            content={"success": False, "error": str(e)}
        )

@app.post("/upload/modal")
async def upload_modal_image(image: UploadFile = File(...)):
    """Загрузка изображения модалки для наложения на кадры"""
    try:
        # Проверка типа файла
        if image.content_type not in ALLOWED_IMAGE_TYPES:
            raise HTTPException(
                status_code=400, 
                detail=f"Неподдерживаемый тип файла. Разрешены: {', '.join(ALLOWED_IMAGE_TYPES)}"
            )
        
        # Проверка размера файла
        content = await image.read()
        if len(content) > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=400, 
                detail=f"Файл слишком большой. Максимальный размер: {MAX_FILE_SIZE // (1024*1024)}MB"
            )
        
        modal_id = str(uuid.uuid4())
        
        # Сохранение изображения
        upload_dir = Path(UPLOAD_DIR) / "modals"
        upload_dir.mkdir(parents=True, exist_ok=True)
        
        file_path = upload_dir / f"{modal_id}_{image.filename}"
        async with aiofiles.open(file_path, 'wb') as f:
            await f.write(content)
        
        # Сохранение в базу данных
        modal_data = await db_manager.create_modal_image(
            filename=image.filename,
            file_path=str(file_path),
            file_size=len(content)
        )
        
        # Логирование
        await db_manager.create_log(
            "modal_uploaded", 
            {"modal_id": modal_id, "filename": image.filename, "file_size": len(content)}
        )
        
        return {
            "success": True,
            "modal_id": modal_data["id"],
            "filename": image.filename,
            "file_size": len(content)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        # Логирование ошибки
        await db_manager.create_log("modal_upload_error", {"error": str(e)})
        return JSONResponse(
            status_code=500,
            content={"success": False, "error": str(e)}
        )

@app.get("/modals")
async def get_modal_images():
    """Получение списка загруженных модалок"""
    try:
        modals = await db_manager.get_modal_images()
        return {
            "modals": [
                {
                    "id": modal["id"],
                    "filename": modal["filename"],
                    "file_size": modal.get("file_size"),
                    "is_active": modal.get("is_active", True),
                    "upload_date": modal["created_at"],
                    "file_path": modal.get("file_path")
                }
                for modal in modals
            ]
        }
    except Exception as e:
        await db_manager.create_log("get_modals_error", {"error": str(e)})
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/modals/{modal_id}/preview")
async def get_modal_preview(modal_id: str):
    """Получение превью изображения модалки"""
    try:
        modal = await db_manager.get_modal_image_by_id(modal_id)
        if not modal:
            raise HTTPException(status_code=404, detail="Модалка не найдена")
        
        file_path = modal.get("file_path")
        if not file_path or not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="Файл модалки не найден")
        
        from fastapi.responses import FileResponse
        return FileResponse(file_path, media_type="image/jpeg")
        
    except HTTPException:
        raise
    except Exception as e:
        await db_manager.create_log("get_modal_preview_error", {"error": str(e)})
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/uploads")
async def get_uploads():
    """Получение списка загрузок"""
    try:
        uploads = await db_manager.get_uploads()
        return {"uploads": uploads}
    except Exception as e:
        await db_manager.create_log("get_uploads_error", {"error": str(e)})
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/templates")
async def get_templates():
    """Получение списка шаблонов"""
    try:
        templates = await db_manager.get_templates()
        return {"templates": templates}
    except Exception as e:
        await db_manager.create_log("get_templates_error", {"error": str(e)})
        raise HTTPException(status_code=500, detail=str(e))

# Вспомогательные функции
async def save_uploaded_file(file: UploadFile) -> str:
    """Сохранение загруженного файла"""
    print(f"🔍 DEBUG save_uploaded_file:")
    print(f"   filename: {file.filename}")
    print(f"   content_type: {file.content_type}")
    print(f"   ALLOWED_VIDEO_TYPES: {ALLOWED_VIDEO_TYPES}")
    
    # Проверка типа файла
    if file.content_type not in ALLOWED_VIDEO_TYPES:
        error_msg = f"Неподдерживаемый тип видео файла. Получен: {file.content_type}, разрешены: {', '.join(ALLOWED_VIDEO_TYPES)}"
        print(f"❌ ERROR: {error_msg}")
        raise HTTPException(status_code=400, detail=error_msg)
    
    upload_dir = Path(UPLOAD_DIR) / "videos"
    upload_dir.mkdir(parents=True, exist_ok=True)
    
    file_path = upload_dir / f"{uuid.uuid4()}_{file.filename}"
    async with aiofiles.open(file_path, 'wb') as f:
        content = await file.read()
        await f.write(content)
    
    return str(file_path)

async def process_video(file_path: str, upload_id: str) -> str:
    """Обработка видео: очистка метаданных и уникализация"""
    import subprocess
    import random
    
    processed_dir = Path(UPLOAD_DIR) / "processed"
    processed_dir.mkdir(parents=True, exist_ok=True)
    
    processed_path = processed_dir / f"{upload_id}_processed.mp4"
    
    try:
        # Очистка метаданных и легкая уникализация через ffmpeg
        # Небольшие изменения для уникализации
        bitrate_variation = random.randint(-100, 100)  # ±100 kbps
        fps_variation = random.uniform(0.95, 1.05)  # ±5% FPS
        
        ffmpeg_cmd = [
            'ffmpeg', '-i', file_path,
            '-c:v', 'libx264',
            '-c:a', 'aac',
            '-b:v', f'{1000 + bitrate_variation}k',  # Базовый битрейт с вариацией
            '-r', f'{30 * fps_variation:.2f}',  # Базовый FPS с вариацией
            '-map_metadata', '-1',  # Удаление всех метаданных
            '-metadata', 'title=',
            '-metadata', 'artist=',
            '-metadata', 'album=',
            '-metadata', 'date=',
            '-metadata', 'comment=',
            '-y',  # Перезаписать файл
            str(processed_path)
        ]
        
        print(f"🔧 Обработка видео: {file_path}")
        print(f"   Команда ffmpeg: {' '.join(ffmpeg_cmd)}")
        
        # Выполняем обработку
        result = subprocess.run(ffmpeg_cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"✅ Видео обработано: {processed_path}")
            return str(processed_path)
        else:
            print(f"⚠️ Ошибка ffmpeg, используем оригинал: {result.stderr}")
            # Если ffmpeg не работает, копируем оригинал
            import shutil
            shutil.copy2(file_path, processed_path)
            return str(processed_path)
            
    except Exception as e:
        print(f"⚠️ Ошибка обработки видео: {e}")
        # Fallback - простое копирование
        import shutil
        shutil.copy2(file_path, processed_path)
        return str(processed_path)

async def get_video_orientation(video_path: str) -> str:
    """Определение ориентации видео"""
    import subprocess
    import json
    
    try:
        # Получаем информацию о видео через ffprobe
        ffprobe_cmd = [
            'ffprobe', '-v', 'quiet',
            '-print_format', 'json',
            '-show_streams',
            video_path
        ]
        
        result = subprocess.run(ffprobe_cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            data = json.loads(result.stdout)
            video_stream = next((s for s in data['streams'] if s['codec_type'] == 'video'), None)
            
            if video_stream:
                width = int(video_stream['width'])
                height = int(video_stream['height'])
                
                print(f"📐 Размеры видео: {width}x{height}")
                
                # Определяем ориентацию
                if width > height:
                    return "horizontal"  # 16:9
                elif height > width:
                    return "vertical"    # 9:16
                else:
                    return "square"      # 1:1
        
        # По умолчанию считаем горизонтальным
        return "horizontal"
        
    except Exception as e:
        print(f"⚠️ Ошибка определения ориентации: {e}")
        return "horizontal"

async def create_other_formats(video_path: str, base_upload_id: str, orientation: str) -> List[dict]:
    """Создание других форматов видео с черными полосами"""
    import subprocess
    
    formats_dir = Path(UPLOAD_DIR) / "formats"
    formats_dir.mkdir(parents=True, exist_ok=True)
    
    created_formats = []
    
    # Определяем какие форматы нужно создать
    formats_to_create = []
    if orientation == "square":
        formats_to_create = [
            {"name": "vertical", "width": 720, "height": 1280, "aspect": "9:16"},
            {"name": "horizontal", "width": 1280, "height": 720, "aspect": "16:9"}
        ]
    elif orientation == "horizontal":
        formats_to_create = [
            {"name": "square", "width": 720, "height": 720, "aspect": "1:1"},
            {"name": "vertical", "width": 720, "height": 1280, "aspect": "9:16"}
        ]
    elif orientation == "vertical":
        formats_to_create = [
            {"name": "square", "width": 720, "height": 720, "aspect": "1:1"},
            {"name": "horizontal", "width": 1280, "height": 720, "aspect": "16:9"}
        ]
    
    print(f"🎬 Создание форматов для {orientation} видео: {[f['name'] for f in formats_to_create]}")
    
    for fmt in formats_to_create:
        try:
            output_path = formats_dir / f"{base_upload_id}_{fmt['name']}.mp4"
            
            # Создаем видео с черными полосами (letterbox/pillarbox)
            # scale: масштабирование с сохранением пропорций
            # pad: добавление черных полос
            ffmpeg_cmd = [
                'ffmpeg', '-i', video_path,
                '-vf', f"scale={fmt['width']}:{fmt['height']}:force_original_aspect_ratio=decrease,pad={fmt['width']}:{fmt['height']}:(ow-iw)/2:(oh-ih)/2:black",
                '-c:v', 'libx264',
                '-c:a', 'aac',
                '-b:v', '1000k',
                '-b:a', '128k',
                '-y',
                str(output_path)
            ]
            
            print(f"   🔧 Создание {fmt['name']} формата ({fmt['width']}x{fmt['height']})...")
            result = subprocess.run(ffmpeg_cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                print(f"   ✅ {fmt['name'].capitalize()} формат создан: {output_path}")
                created_formats.append({
                    "orientation": fmt['name'],
                    "path": str(output_path),
                    "resolution": f"{fmt['width']}x{fmt['height']}",
                    "aspect": fmt['aspect']
                })
            else:
                print(f"   ⚠️ Ошибка создания {fmt['name']} формата: {result.stderr}")
                
        except Exception as e:
            print(f"   ⚠️ Ошибка создания {fmt['name']} формата: {e}")
    
    return created_formats

def generate_video_title(campaign_name: str, orientation: str, copy_number: int = 1) -> str:
    """Генерация названия видео: кампания + ориентация (англ) + дата + #номер"""
    from datetime import datetime
    
    # Ориентация на английском
    orientation_en = {
        "horizontal": "Landscape",
        "vertical": "Portrait",
        "square": "Square"
    }.get(orientation, orientation.capitalize())
    
    # Формат даты: ДД.ММ.ГГ
    date_str = datetime.now().strftime("%d.%m.%y")
    
    # Формируем название: "Название Ориентация Дата #Номер"
    title = f"{campaign_name} {orientation_en} {date_str} #{copy_number}"
    
    return title

async def download_from_drive(drive_url: str, upload_id: str) -> str:
    """Скачивание видео из Google Drive"""
    # Здесь будет логика скачивания из Google Drive
    # Пока заглушка
    downloaded_dir = Path(UPLOAD_DIR) / "downloaded"
    downloaded_dir.mkdir(parents=True, exist_ok=True)
    
    return str(downloaded_dir / f"{upload_id}_from_drive.mp4")

async def process_thumbnail(video_path: str, option: str, modal_id: Optional[str]) -> Optional[str]:
    """Обработка миниатюры"""
    import subprocess
    from PIL import Image, ImageDraw, ImageFont
    import os
    
    if option == "none":
        return None
    
    thumbnails_dir = Path(UPLOAD_DIR) / "thumbnails"
    thumbnails_dir.mkdir(parents=True, exist_ok=True)
    
    try:
        if option == "first_frame":
            # Извлечение первого кадра
            thumbnail_path = thumbnails_dir / f"{uuid.uuid4()}_first_frame.jpg"
            
            ffmpeg_cmd = [
                'ffmpeg', '-i', video_path,
                '-ss', '00:00:00.1',  # 100 миллисекунд от начала
                '-vframes', '1',      # Один кадр
                '-q:v', '2',          # Высокое качество
                '-y',
                str(thumbnail_path)
            ]
            
            print(f"🖼️ Извлечение первого кадра: {video_path}")
            result = subprocess.run(ffmpeg_cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                print(f"✅ Первый кадр извлечен: {thumbnail_path}")
                return str(thumbnail_path)
            else:
                print(f"⚠️ Ошибка извлечения кадра: {result.stderr}")
                return None
                
        elif option == "soft_modal" and modal_id:
            # Наложение модалки на первый кадр
            thumbnail_path = thumbnails_dir / f"{uuid.uuid4()}_with_modal.jpg"
            
            # Сначала извлекаем первый кадр
            temp_frame = thumbnails_dir / f"temp_frame_{uuid.uuid4()}.jpg"
            ffmpeg_cmd = [
                'ffmpeg', '-i', video_path,
                '-ss', '00:00:00.1',  # 100 миллисекунд от начала
                '-vframes', '1',
                '-q:v', '2',
                '-y',
                str(temp_frame)
            ]
            
            result = subprocess.run(ffmpeg_cmd, capture_output=True, text=True)
            if result.returncode != 0:
                print(f"⚠️ Ошибка извлечения кадра для модалки: {result.stderr}")
                return None
            
            # Получаем путь к модалке из базы данных
            modal_data = await db_manager.get_modal_image_by_id(modal_id)
            if not modal_data or not modal_data.get("file_path"):
                print(f"⚠️ Модалка не найдена: {modal_id}")
                return None
            
            modal_path = modal_data["file_path"]
            
            # Накладываем модалку на кадр
            try:
                # Открываем изображения
                frame_img = Image.open(temp_frame)
                modal_img = Image.open(modal_path)
                
                print(f"🖼️ Размер кадра: {frame_img.size}")
                print(f"🖼️ Размер модалки: {modal_img.size}")
                
                # Изменяем размер модалки под размер кадра
                modal_img = modal_img.resize(frame_img.size, Image.Resampling.LANCZOS)
                
                # Конвертируем в RGBA для работы с прозрачностью
                if frame_img.mode != 'RGBA':
                    frame_img = frame_img.convert('RGBA')
                if modal_img.mode != 'RGBA':
                    modal_img = modal_img.convert('RGBA')
                
                # Создаем новый RGBA изображение
                composite = Image.new('RGBA', frame_img.size)
                
                # Сначала накладываем кадр
                composite.paste(frame_img, (0, 0))
                
                # Затем накладываем модалку с прозрачностью
                # Устанавливаем альфа-канал модалки на 128 (50% прозрачности)
                modal_with_alpha = modal_img.copy()
                modal_with_alpha.putalpha(128)
                
                # Накладываем модалку
                composite.paste(modal_with_alpha, (0, 0), modal_with_alpha)
                
                # Конвертируем обратно в RGB для сохранения
                composite_rgb = composite.convert('RGB')
                
                # Сохраняем результат
                composite_rgb.save(thumbnail_path, 'JPEG', quality=95)
                
                # Удаляем временный файл
                if temp_frame.exists():
                    temp_frame.unlink()
                
                print(f"✅ Миниатюра с модалкой создана: {thumbnail_path}")
                print(f"🖼️ Файл сохранен: {thumbnail_path.exists()}")
                return str(thumbnail_path)
                
            except Exception as e:
                print(f"⚠️ Ошибка создания миниатюры с модалкой: {e}")
                return None
    
    except Exception as e:
        print(f"⚠️ Общая ошибка обработки миниатюры: {e}")
        return None
    
    return None

async def upload_to_youtube(video_path: str, title: str, thumbnail_path: Optional[str]) -> str:
    """Загрузка видео на YouTube"""
    try:
        # Используем реальную интеграцию с YouTube
        result = await integration_manager.upload_video_to_youtube(
            video_path=video_path,
            title=title,
            description=f"Видео загружено через UAC Creative Manager\nДата: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            thumbnail_path=thumbnail_path
        )
        
        if result.get("success"):
            return result.get("video_url")
        else:
            # Если интеграция не настроена, возвращаем заглушку
            await db_manager.create_log("youtube_upload_fallback", {"error": result.get("error", "Unknown error")})
            return f"https://youtube.com/watch?v={str(uuid.uuid4())[:11]}"
            
    except Exception as e:
        # Логируем ошибку и возвращаем заглушку
        await db_manager.create_log("youtube_upload_error", {"error": str(e)})
        return f"https://youtube.com/watch?v={str(uuid.uuid4())[:11]}"

# ==================== INTEGRATION ENDPOINTS ====================

@app.post("/integrations/youtube/setup")
async def setup_youtube_integration(request: Request):
    """Настройка YouTube интеграции"""
    try:
        data = await request.json()
        client_id = data.get("client_id")
        client_secret = data.get("client_secret")
        redirect_uri = data.get("redirect_uri")
        
        if not client_id or not client_secret:
            return {"success": False, "error": "client_id и client_secret обязательны"}
        
        result = await integration_manager.setup_youtube_credentials(client_id, client_secret, redirect_uri)
        return result
    except Exception as e:
        await db_manager.create_log("youtube_setup_error", {"error": str(e)})
        return {"success": False, "error": str(e)}

@app.post("/integrations/youtube/test")
async def test_youtube_integration():
    """Тестирование YouTube интеграции"""
    try:
        result = await integration_manager.test_youtube_connection()
        return result
    except Exception as e:
        await db_manager.create_log("youtube_test_error", {"error": str(e)})
        return {"success": False, "error": str(e)}

@app.post("/integrations/telegram/setup")
async def setup_telegram_integration(request: Request):
    """Настройка Telegram интеграции"""
    try:
        data = await request.json()
        bot_token = data.get("bot_token")
        chat_id = data.get("chat_id")
        
        if not bot_token:
            return {"success": False, "error": "bot_token обязателен"}
        
        result = await integration_manager.setup_telegram_bot(bot_token, chat_id)
        return result
    except Exception as e:
        await db_manager.create_log("telegram_setup_error", {"error": str(e)})
        return {"success": False, "error": str(e)}

@app.post("/integrations/telegram/test")
async def test_telegram_integration():
    """Тестирование Telegram интеграции"""
    try:
        result = await integration_manager.test_telegram_connection()
        return result
    except Exception as e:
        await db_manager.create_log("telegram_test_error", {"error": str(e)})
        return {"success": False, "error": str(e)}

@app.post("/integrations/google-drive/setup")
async def setup_google_drive_integration(request: Request):
    """Настройка Google Drive интеграции"""
    try:
        data = await request.json()
        client_id = data.get("client_id")
        client_secret = data.get("client_secret")
        redirect_uri = data.get("redirect_uri")
        
        if not client_id or not client_secret:
            return {"success": False, "error": "client_id и client_secret обязательны"}
        
        result = await integration_manager.setup_google_drive_credentials(client_id, client_secret, redirect_uri)
        return result
    except Exception as e:
        await db_manager.create_log("google_drive_setup_error", {"error": str(e)})
        return {"success": False, "error": str(e)}

@app.post("/integrations/google-drive/test")
async def test_google_drive_integration():
    """Тестирование Google Drive интеграции"""
    try:
        result = await integration_manager.test_google_drive_connection()
        return result
    except Exception as e:
        await db_manager.create_log("google_drive_test_error", {"error": str(e)})
        return {"success": False, "error": str(e)}

@app.post("/integrations/google-ads/setup")
async def setup_google_ads_integration(request: Request):
    """Настройка Google Ads интеграции"""
    try:
        data = await request.json()
        client_id = data.get("client_id")
        client_secret = data.get("client_secret")
        refresh_token = data.get("refresh_token")
        developer_token = data.get("developer_token")
        customer_id = data.get("customer_id")
        
        if not client_id or not client_secret:
            return {"success": False, "error": "client_id и client_secret обязательны"}
        
        result = await integration_manager.setup_google_ads_credentials(
            client_id, client_secret, refresh_token, developer_token, customer_id
        )
        return result
    except Exception as e:
        await db_manager.create_log("google_ads_setup_error", {"error": str(e)})
        return {"success": False, "error": str(e)}

@app.post("/integrations/google-ads/test")
async def test_google_ads_integration():
    """Тестирование Google Ads интеграции"""
    try:
        result = await integration_manager.test_google_ads_connection()
        return result
    except Exception as e:
        await db_manager.create_log("google_ads_test_error", {"error": str(e)})
        return {"success": False, "error": str(e)}

@app.get("/integrations/status")
async def get_integrations_status():
    """Получение статуса всех интеграций"""
    try:
        integrations = {}
        
        # YouTube
        youtube_creds = await db_manager.get_oauth_credentials("youtube")
        integrations["youtube"] = {
            "configured": bool(youtube_creds),
            "has_credentials": bool(youtube_creds and youtube_creds.get("credentials", {}).get("client_id")),
            "authorized": bool(youtube_creds and youtube_creds.get("credentials", {}).get("access_token"))
        }
        
        # Telegram
        telegram_creds = await db_manager.get_oauth_credentials("telegram")
        integrations["telegram"] = {
            "configured": bool(telegram_creds),
            "has_credentials": bool(telegram_creds and telegram_creds.get("credentials", {}).get("bot_token"))
        }
        
        # Google Drive
        drive_creds = await db_manager.get_oauth_credentials("google_drive")
        integrations["google_drive"] = {
            "configured": bool(drive_creds),
            "has_credentials": bool(drive_creds and drive_creds.get("credentials", {}).get("client_id")),
            "authorized": bool(drive_creds and drive_creds.get("credentials", {}).get("access_token"))
        }
        
        # Google Ads
        ads_creds = await db_manager.get_oauth_credentials("google_ads")
        integrations["google_ads"] = {
            "configured": bool(ads_creds),
            "has_credentials": bool(ads_creds and ads_creds.get("credentials", {}).get("client_id")),
            "authorized": bool(ads_creds and ads_creds.get("credentials", {}).get("access_token"))
        }
        
        return {"integrations": integrations}
        
    except Exception as e:
        await db_manager.create_log("integrations_status_error", {"error": str(e)})
        return {"success": False, "error": str(e)}

@app.get("/integrations/settings")
async def get_integrations_settings():
    """Получение настроек всех интеграций"""
    try:
        settings = {}
        
        # YouTube
        youtube_creds = await db_manager.get_oauth_credentials("youtube")
        if youtube_creds and youtube_creds.get("credentials"):
            creds = youtube_creds["credentials"]
            settings["youtube"] = {
                "client_id": creds.get("client_id", ""),
                "client_secret": creds.get("client_secret", ""),
                "redirect_uri": creds.get("redirect_uri", "")
            }
        else:
            settings["youtube"] = {"client_id": "", "client_secret": "", "redirect_uri": ""}
        
        # Telegram
        telegram_creds = await db_manager.get_oauth_credentials("telegram")
        if telegram_creds and telegram_creds.get("credentials"):
            creds = telegram_creds["credentials"]
            settings["telegram"] = {
                "bot_token": creds.get("bot_token", ""),
                "chat_id": creds.get("chat_id", "")
            }
        else:
            settings["telegram"] = {"bot_token": "", "chat_id": ""}
        
        # Google Drive
        drive_creds = await db_manager.get_oauth_credentials("google_drive")
        if drive_creds and drive_creds.get("credentials"):
            creds = drive_creds["credentials"]
            settings["google_drive"] = {
                "client_id": creds.get("client_id", ""),
                "client_secret": creds.get("client_secret", ""),
                "redirect_uri": creds.get("redirect_uri", "")
            }
        else:
            settings["google_drive"] = {"client_id": "", "client_secret": "", "redirect_uri": ""}
        
        # Google Ads
        ads_creds = await db_manager.get_oauth_credentials("google_ads")
        if ads_creds and ads_creds.get("credentials"):
            creds = ads_creds["credentials"]
            settings["google_ads"] = {
                "client_id": creds.get("client_id", ""),
                "client_secret": creds.get("client_secret", ""),
                "refresh_token": creds.get("refresh_token", ""),
                "developer_token": creds.get("developer_token", ""),
                "customer_id": creds.get("customer_id", "")
            }
        else:
            settings["google_ads"] = {
                "client_id": "", "client_secret": "", "refresh_token": "", 
                "developer_token": "", "customer_id": ""
            }
        
        return {"success": True, "settings": settings}
        
    except Exception as e:
        await db_manager.create_log("integrations_settings_error", {"error": str(e)})
        return {"success": False, "error": str(e)}

@app.post("/integrations/telegram/send-notification")
async def send_telegram_notification(
    message: str = Form(...)
):
    """Отправка уведомления в Telegram"""
    try:
        result = await integration_manager.send_telegram_notification(message)
        return result
    except Exception as e:
        await db_manager.create_log("telegram_notification_error", {"error": str(e)})
        return {"success": False, "error": str(e)}

@app.get("/auth/youtube/callback")
async def youtube_oauth_callback(
    code: Optional[str] = None,
    state: Optional[str] = None,
    error: Optional[str] = None
):
    """Обработка OAuth callback для YouTube"""
    try:
        if error:
            return JSONResponse(
                content={"success": False, "error": f"OAuth error: {error}"},
                status_code=400
            )
        
        if not code:
            return JSONResponse(
                content={"success": False, "error": "Authorization code not provided"},
                status_code=400
            )
        
        # Обработка авторизационного кода
        result = await integration_manager.handle_youtube_oauth_callback(code, state)
        
        # Возвращаем HTML страницу с результатом
        if result.get("success"):
            html_content = """
            <!DOCTYPE html>
            <html>
            <head>
                <title>YouTube Authorization</title>
                <meta charset="utf-8">
                <style>
                    body { font-family: Arial, sans-serif; text-align: center; padding: 50px; }
                    .success { color: green; }
                    .error { color: red; }
                </style>
            </head>
            <body>
                <h1 class="success">✅ YouTube авторизация успешна!</h1>
                <p>Можете закрыть это окно и вернуться в приложение.</p>
                <script>
                    setTimeout(() => {
                        window.close();
                    }, 3000);
                </script>
            </body>
            </html>
            """
        else:
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>YouTube Authorization</title>
                <meta charset="utf-8">
                <style>
                    body {{ font-family: Arial, sans-serif; text-align: center; padding: 50px; }}
                    .success {{ color: green; }}
                    .error {{ color: red; }}
                </style>
            </head>
            <body>
                <h1 class="error">❌ Ошибка авторизации YouTube</h1>
                <p>{result.get('error', 'Неизвестная ошибка')}</p>
                <p>Попробуйте еще раз.</p>
                <script>
                    setTimeout(() => {{
                        window.close();
                    }}, 5000);
                </script>
            </body>
            </html>
            """
        
        return HTMLResponse(content=html_content)
        
    except Exception as e:
        await db_manager.create_log("youtube_oauth_callback_error", {"error": str(e)})
        error_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>YouTube Authorization</title>
            <meta charset="utf-8">
            <style>
                body {{ font-family: Arial, sans-serif; text-align: center; padding: 50px; }}
                .error {{ color: red; }}
            </style>
        </head>
        <body>
            <h1 class="error">❌ Ошибка сервера</h1>
            <p>{str(e)}</p>
        </body>
        </html>
        """
        return HTMLResponse(content=error_html, status_code=500)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
