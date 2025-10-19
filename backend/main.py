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
        
        # Сохранение в базу данных
        upload_data = {
            "youtube_url": youtube_url,
            "video_title": video_title,
            "campaign_name": campaign_name,
            "thumbnail_type": thumbnail_option,
            "thumbnail_image_id": formData.modal_image_id if thumbnail_option == "custom_modal" else None,
            "status": "active"
        }
        
        upload_record = await db_manager.create_upload(upload_data)
        
        # Логирование успешной загрузки
        await db_manager.create_log(
            "video_uploaded",
            {
                "upload_id": upload_record["id"],
                "campaign_name": campaign_name,
                "youtube_url": youtube_url,
                "thumbnail_type": thumbnail_option
            }
        )
        
        return {
            "success": True,
            "upload_id": upload_record["id"],
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
                    "upload_date": modal["created_at"]
                }
                for modal in modals
            ]
        }
    except Exception as e:
        await db_manager.create_log("get_modals_error", {"error": str(e)})
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
    # Проверка типа файла
    if file.content_type not in ALLOWED_VIDEO_TYPES:
        raise HTTPException(
            status_code=400, 
            detail=f"Неподдерживаемый тип видео файла. Разрешены: {', '.join(ALLOWED_VIDEO_TYPES)}"
        )
    
    upload_dir = Path(UPLOAD_DIR) / "videos"
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
    processed_dir = Path(UPLOAD_DIR) / "processed"
    processed_dir.mkdir(parents=True, exist_ok=True)
    
    processed_path = processed_dir / f"{upload_id}_processed.mp4"
    
    # Заглушка - простое копирование
    import shutil
    shutil.copy2(file_path, processed_path)
    
    return str(processed_path)

async def download_from_drive(drive_url: str, upload_id: str) -> str:
    """Скачивание видео из Google Drive"""
    # Здесь будет логика скачивания из Google Drive
    # Пока заглушка
    downloaded_dir = Path(UPLOAD_DIR) / "downloaded"
    downloaded_dir.mkdir(parents=True, exist_ok=True)
    
    return str(downloaded_dir / f"{upload_id}_from_drive.mp4")

async def process_thumbnail(video_path: str, option: str, modal_id: Optional[str]) -> Optional[str]:
    """Обработка миниатюры"""
    if option == "none":
        return None
    
    thumbnails_dir = Path(UPLOAD_DIR) / "thumbnails"
    thumbnails_dir.mkdir(parents=True, exist_ok=True)
    
    if option == "first_frame":
        # Извлечение первого кадра
        return str(thumbnails_dir / f"{uuid.uuid4()}_first_frame.jpg")
    elif option == "custom_modal" and modal_id:
        # Наложение модалки на первый кадр
        return str(thumbnails_dir / f"{uuid.uuid4()}_with_modal.jpg")
    
    return None

async def upload_to_youtube(video_path: str, title: str, thumbnail_path: Optional[str]) -> str:
    """Загрузка видео на YouTube"""
    # TODO: Здесь будет интеграция с YouTube Data API
    # Пока возвращаем заглушку для демонстрации
    import time
    await asyncio.sleep(1)  # Имитация загрузки
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
