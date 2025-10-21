"""
Модуль для управления интеграциями с внешними сервисами
"""
import asyncio
import json
import os
from typing import Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
import httpx
import telegram
from telegram import Bot
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from database import db_manager
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class IntegrationManager:
    """Менеджер интеграций с внешними сервисами"""
    
    def __init__(self):
        self.youtube_service = None
        self.telegram_bot = None
        
    # ==================== YOUTUBE INTEGRATION ====================
    
    async def setup_youtube_credentials(self, client_id: str, client_secret: str, redirect_uri: str) -> Dict[str, Any]:
        """Настройка YouTube OAuth2 credentials"""
        try:
            credentials_data = {
                "client_id": client_id,
                "client_secret": client_secret,
                "redirect_uri": redirect_uri,
                "scopes": [
                    "https://www.googleapis.com/auth/youtube.upload",
                    "https://www.googleapis.com/auth/youtube.readonly"
                ]
            }
            
            # Сохранение в БД
            result = await db_manager.save_oauth_credentials("youtube", credentials_data)
            
            # Логирование
            await db_manager.create_log(
                "youtube_credentials_saved",
                {"client_id": client_id, "has_secret": bool(client_secret)}
            )
            
            return {
                "success": True,
                "message": "YouTube credentials сохранены",
                "auth_url": self._get_youtube_auth_url(client_id, redirect_uri, client_secret)
            }
            
        except Exception as e:
            logger.error(f"YouTube credentials setup error: {e}")
            await db_manager.create_log("youtube_credentials_error", {"error": str(e)})
            return {"success": False, "error": str(e)}
    
    async def handle_youtube_oauth_callback(self, code: str, state: str) -> Dict[str, Any]:
        """Обработка OAuth callback для YouTube"""
        try:
            # Получаем сохраненные credentials
            credentials = await db_manager.get_oauth_credentials("youtube")
            if not credentials:
                return {"success": False, "error": "YouTube credentials not found"}
            
            # Извлекаем данные из credentials
            creds_data = credentials.get("credentials", {})
            client_id = creds_data.get("client_id")
            client_secret = creds_data.get("client_secret")
            redirect_uri = creds_data.get("redirect_uri")
            scopes = creds_data.get("scopes", [
                "https://www.googleapis.com/auth/youtube.upload",
                "https://www.googleapis.com/auth/youtube.readonly"
            ])
            
            if not client_id or not client_secret:
                return {"success": False, "error": "Не найдены client_id или client_secret в настройках"}
            
            # Создаем flow для обмена кода на токен
            flow = Flow.from_client_config(
                {
                    "web": {
                        "client_id": client_id,
                        "client_secret": client_secret,
                        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                        "token_uri": "https://oauth2.googleapis.com/token",
                        "redirect_uris": [redirect_uri]
                    }
                },
                scopes=scopes
            )
            flow.redirect_uri = redirect_uri
            
            # Обмениваем код на токен
            flow.fetch_token(code=code)
            
            # Сохраняем токены
            token_data = {
                "access_token": flow.credentials.token,
                "refresh_token": flow.credentials.refresh_token,
                "token_uri": flow.credentials.token_uri,
                "client_id": flow.credentials.client_id,
                "client_secret": flow.credentials.client_secret,
                "scopes": flow.credentials.scopes,
                "expiry": flow.credentials.expiry.isoformat() if flow.credentials.expiry else None
            }
            
            await db_manager.save_oauth_credentials("youtube", token_data)
            
            # Логирование
            await db_manager.create_log(
                "youtube_oauth_success",
                {"has_access_token": bool(flow.credentials.token)}
            )
            
            return {"success": True, "message": "YouTube авторизация успешна"}
            
        except Exception as e:
            logger.error(f"YouTube OAuth callback error: {e}")
            await db_manager.create_log("youtube_oauth_callback_error", {"error": str(e)})
            return {"success": False, "error": str(e)}
    
    def _get_youtube_auth_url(self, client_id: str, redirect_uri: str, client_secret: str = "") -> str:
        """Получение URL для авторизации YouTube"""
        flow = Flow.from_client_config(
            {
                "web": {
                    "client_id": client_id,
                    "client_secret": client_secret,
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                    "redirect_uris": [redirect_uri]
                }
            },
            scopes=[
                "https://www.googleapis.com/auth/youtube.upload",
                "https://www.googleapis.com/auth/youtube.readonly"
            ]
        )
        flow.redirect_uri = redirect_uri
        return flow.authorization_url()[0]
    
    async def test_youtube_connection(self) -> Dict[str, Any]:
        """Тестирование подключения к YouTube API"""
        try:
            # Получение credentials из БД
            credentials = await db_manager.get_oauth_credentials("youtube")
            if not credentials:
                return {"success": False, "error": "YouTube credentials не настроены"}
            
            # Проверка наличия токенов
            creds_data = credentials.get("credentials", {})
            if not creds_data.get("access_token"):
                return {"success": False, "error": "YouTube не авторизован. Выполните авторизацию."}
            
            # Создание сервиса YouTube
            creds = Credentials(
                token=creds_data.get("access_token"),
                refresh_token=creds_data.get("refresh_token"),
                token_uri="https://oauth2.googleapis.com/token",
                client_id=creds_data.get("client_id"),
                client_secret=creds_data.get("client_secret")
            )
            
            service = build('youtube', 'v3', credentials=creds)
            
            # Тестовый запрос
            request = service.channels().list(part="snippet", mine=True)
            response = request.execute()
            
            await db_manager.create_log("youtube_connection_test", {"success": True})
            
            return {
                "success": True,
                "message": "YouTube подключение успешно",
                "channel_info": response.get("items", [{}])[0].get("snippet", {})
            }
            
        except HttpError as e:
            error_msg = f"YouTube API error: {e}"
            logger.error(error_msg)
            await db_manager.create_log("youtube_connection_error", {"error": error_msg})
            return {"success": False, "error": error_msg}
        except Exception as e:
            error_msg = f"YouTube connection error: {e}"
            logger.error(error_msg)
            await db_manager.create_log("youtube_connection_error", {"error": error_msg})
            return {"success": False, "error": error_msg}
    
    async def upload_video_to_youtube(self, video_path: str, title: str, description: str = "", thumbnail_path: str = None) -> Dict[str, Any]:
        """Загрузка видео на YouTube"""
        try:
            credentials = await db_manager.get_oauth_credentials("youtube")
            if not credentials:
                return {"success": False, "error": "YouTube credentials не настроены"}
            
            creds_data = credentials.get("credentials", {})
            creds = Credentials(
                token=creds_data.get("access_token"),
                refresh_token=creds_data.get("refresh_token"),
                token_uri="https://oauth2.googleapis.com/token",
                client_id=creds_data.get("client_id"),
                client_secret=creds_data.get("client_secret")
            )
            
            service = build('youtube', 'v3', credentials=creds)
            
            # Подготовка метаданных видео
            body = {
                'snippet': {
                    'title': title,
                    'description': description,
                    'tags': ['UAC Creative Manager'],
                    'categoryId': '22'  # People & Blogs
                },
                'status': {
                    'privacyStatus': 'unlisted',  # Unlisted вместо private
                    'madeForKids': False,  # Видео не для детей
                    'selfDeclaredMadeForKids': False
                }
            }
            
            # Загрузка видео
            media_body = service.videos().insert(
                part=','.join(body.keys()),
                body=body,
                media_body=video_path
            )
            
            # Выполнение загрузки
            response = media_body.execute()
            video_id = response['id']
            video_url = f"https://www.youtube.com/watch?v={video_id}"
            
            # Загрузка миниатюры, если она создана
            if thumbnail_path and os.path.exists(thumbnail_path):
                try:
                    print(f"🖼️ Загрузка миниатюры: {thumbnail_path}")
                    service.thumbnails().set(
                        videoId=video_id,
                        media_body=thumbnail_path
                    ).execute()
                    print(f"✅ Миниатюра загружена для видео {video_id}")
                except Exception as e:
                    print(f"⚠️ Ошибка загрузки миниатюры: {e}")
                    # Продолжаем без миниатюры
            
            await db_manager.create_log(
                "video_uploaded_to_youtube",
                {"video_id": video_id, "title": title, "url": video_url}
            )
            
            return {
                "success": True,
                "video_id": video_id,
                "video_url": video_url,
                "response": response
            }
            
        except Exception as e:
            error_msg = f"YouTube upload error: {e}"
            logger.error(error_msg)
            await db_manager.create_log("youtube_upload_error", {"error": error_msg})
            return {"success": False, "error": error_msg}
    
    # ==================== TELEGRAM INTEGRATION ====================
    
    async def setup_telegram_bot(self, bot_token: str, chat_id: str) -> Dict[str, Any]:
        """Настройка Telegram Bot"""
        try:
            # Тестирование токена
            bot = Bot(token=bot_token)
            bot_info = await bot.get_me()
            
            credentials_data = {
                "bot_token": bot_token,
                "chat_id": chat_id,
                "bot_username": bot_info.username,
                "bot_first_name": bot_info.first_name
            }
            
            # Сохранение в БД
            result = await db_manager.save_oauth_credentials("telegram", credentials_data)
            
            # Логирование
            await db_manager.create_log(
                "telegram_bot_saved",
                {"bot_username": bot_info.username, "chat_id": chat_id}
            )
            
            return {
                "success": True,
                "message": "Telegram Bot настроен успешно",
                "bot_info": {
                    "username": bot_info.username,
                    "first_name": bot_info.first_name,
                    "id": bot_info.id
                }
            }
            
        except Exception as e:
            error_msg = f"Telegram Bot setup error: {e}"
            logger.error(error_msg)
            await db_manager.create_log("telegram_bot_error", {"error": error_msg})
            return {"success": False, "error": error_msg}
    
    async def test_telegram_connection(self) -> Dict[str, Any]:
        """Тестирование подключения к Telegram"""
        try:
            credentials = await db_manager.get_oauth_credentials("telegram")
            if not credentials:
                return {"success": False, "error": "Telegram Bot не настроен"}
            
            creds_data = credentials.get("credentials", {})
            bot_token = creds_data.get("bot_token")
            chat_id = creds_data.get("chat_id")
            
            if not bot_token:
                return {"success": False, "error": "Telegram Bot токен не найден"}
            
            # Тестирование бота
            bot = Bot(token=bot_token)
            bot_info = await bot.get_me()
            
            # Тестирование отправки сообщения (если указан chat_id)
            if chat_id:
                try:
                    test_message = f"🧪 Тест подключения UAC Creative Manager\nВремя: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                    await bot.send_message(chat_id=chat_id, text=test_message)
                    message_sent = True
                except Exception as e:
                    message_sent = False
                    logger.warning(f"Не удалось отправить тестовое сообщение: {e}")
            else:
                message_sent = None
            
            await db_manager.create_log("telegram_connection_test", {"success": True, "message_sent": message_sent})
            
            return {
                "success": True,
                "message": "Telegram подключение успешно",
                "bot_info": {
                    "username": bot_info.username,
                    "first_name": bot_info.first_name,
                    "id": bot_info.id
                },
                "message_sent": message_sent
            }
            
        except Exception as e:
            error_msg = f"Telegram connection error: {e}"
            logger.error(error_msg)
            await db_manager.create_log("telegram_connection_error", {"error": error_msg})
            return {"success": False, "error": error_msg}
    
    async def send_telegram_notification(self, message: str, parse_mode: str = "HTML") -> Dict[str, Any]:
        """Отправка уведомления в Telegram"""
        try:
            credentials = await db_manager.get_oauth_credentials("telegram")
            if not credentials:
                return {"success": False, "error": "Telegram Bot не настроен"}
            
            creds_data = credentials.get("credentials", {})
            bot_token = creds_data.get("bot_token")
            chat_id = creds_data.get("chat_id")
            
            if not bot_token or not chat_id:
                return {"success": False, "error": "Telegram Bot токен или chat_id не настроены"}
            
            bot = Bot(token=bot_token)
            await bot.send_message(chat_id=chat_id, text=message, parse_mode=parse_mode)
            
            await db_manager.create_log("telegram_notification_sent", {"message_length": len(message)})
            
            return {"success": True, "message": "Уведомление отправлено"}
            
        except Exception as e:
            error_msg = f"Telegram notification error: {e}"
            logger.error(error_msg)
            await db_manager.create_log("telegram_notification_error", {"error": error_msg})
            return {"success": False, "error": error_msg}
    
    # ==================== GOOGLE DRIVE INTEGRATION ====================
    
    async def setup_google_drive_credentials(self, client_id: str, client_secret: str, redirect_uri: str) -> Dict[str, Any]:
        """Настройка Google Drive OAuth2 credentials"""
        try:
            credentials_data = {
                "client_id": client_id,
                "client_secret": client_secret,
                "redirect_uri": redirect_uri,
                "scopes": [
                    "https://www.googleapis.com/auth/drive.readonly",
                    "https://www.googleapis.com/auth/drive.file"
                ]
            }
            
            # Сохранение в БД
            result = await db_manager.save_oauth_credentials("google_drive", credentials_data)
            
            # Логирование
            await db_manager.create_log(
                "google_drive_credentials_saved",
                {"client_id": client_id, "has_secret": bool(client_secret)}
            )
            
            return {
                "success": True,
                "message": "Google Drive credentials сохранены",
                "auth_url": self._get_google_drive_auth_url(client_id, redirect_uri)
            }
            
        except Exception as e:
            error_msg = f"Google Drive credentials setup error: {e}"
            logger.error(error_msg)
            await db_manager.create_log("google_drive_credentials_error", {"error": error_msg})
            return {"success": False, "error": error_msg}
    
    def _get_google_drive_auth_url(self, client_id: str, redirect_uri: str) -> str:
        """Получение URL для авторизации Google Drive"""
        flow = Flow.from_client_config(
            {
                "web": {
                    "client_id": client_id,
                    "client_secret": "",
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                    "redirect_uris": [redirect_uri]
                }
            },
            scopes=[
                "https://www.googleapis.com/auth/drive.readonly",
                "https://www.googleapis.com/auth/drive.file"
            ]
        )
        flow.redirect_uri = redirect_uri
        return flow.authorization_url()[0]
    
    async def test_google_drive_connection(self) -> Dict[str, Any]:
        """Тестирование подключения к Google Drive API"""
        try:
            credentials = await db_manager.get_oauth_credentials("google_drive")
            if not credentials:
                return {"success": False, "error": "Google Drive credentials не настроены"}
            
            creds_data = credentials.get("credentials", {})
            if not creds_data.get("access_token"):
                return {"success": False, "error": "Google Drive не авторизован. Выполните авторизацию."}
            
            # Создание сервиса Google Drive
            creds = Credentials(
                token=creds_data.get("access_token"),
                refresh_token=creds_data.get("refresh_token"),
                token_uri="https://oauth2.googleapis.com/token",
                client_id=creds_data.get("client_id"),
                client_secret=creds_data.get("client_secret")
            )
            
            service = build('drive', 'v3', credentials=creds)
            
            # Тестовый запрос - получение информации о пользователе
            about = service.about().get(fields="user").execute()
            
            await db_manager.create_log("google_drive_connection_test", {"success": True})
            
            return {
                "success": True,
                "message": "Google Drive подключение успешно",
                "user_info": about.get("user", {})
            }
            
        except Exception as e:
            error_msg = f"Google Drive connection error: {e}"
            logger.error(error_msg)
            await db_manager.create_log("google_drive_connection_error", {"error": error_msg})
            return {"success": False, "error": error_msg}
    
    async def download_from_google_drive(self, file_id: str) -> Dict[str, Any]:
        """Скачивание файла из Google Drive"""
        try:
            credentials = await db_manager.get_oauth_credentials("google_drive")
            if not credentials:
                return {"success": False, "error": "Google Drive credentials не настроены"}
            
            creds_data = credentials.get("credentials", {})
            creds = Credentials(
                token=creds_data.get("access_token"),
                refresh_token=creds_data.get("refresh_token"),
                token_uri="https://oauth2.googleapis.com/token",
                client_id=creds_data.get("client_id"),
                client_secret=creds_data.get("client_secret")
            )
            
            service = build('drive', 'v3', credentials=creds)
            
            # Получение информации о файле
            file_metadata = service.files().get(fileId=file_id).execute()
            
            # Скачивание файла
            request = service.files().get_media(fileId=file_id)
            file_content = request.execute()
            
            await db_manager.create_log(
                "file_downloaded_from_drive",
                {"file_id": file_id, "file_name": file_metadata.get("name")}
            )
            
            return {
                "success": True,
                "file_content": file_content,
                "file_metadata": file_metadata
            }
            
        except Exception as e:
            error_msg = f"Google Drive download error: {e}"
            logger.error(error_msg)
            await db_manager.create_log("google_drive_download_error", {"error": error_msg})
            return {"success": False, "error": error_msg}
    
    # ==================== GOOGLE ADS INTEGRATION ====================
    
    async def setup_google_ads_credentials(self, client_id: str, client_secret: str, refresh_token: str, developer_token: str, customer_id: str) -> Dict[str, Any]:
        """Настройка Google Ads API credentials"""
        try:
            credentials_data = {
                "client_id": client_id,
                "client_secret": client_secret,
                "refresh_token": refresh_token,
                "developer_token": developer_token,
                "customer_id": customer_id,
                "scopes": [
                    "https://www.googleapis.com/auth/adwords"
                ]
            }
            
            # Сохранение в БД
            result = await db_manager.save_oauth_credentials("google_ads", credentials_data)
            
            # Логирование
            await db_manager.create_log(
                "google_ads_credentials_saved",
                {"client_id": client_id, "customer_id": customer_id, "has_developer_token": bool(developer_token)}
            )
            
            return {
                "success": True,
                "message": "Google Ads credentials сохранены"
            }
            
        except Exception as e:
            error_msg = f"Google Ads credentials setup error: {e}"
            logger.error(error_msg)
            await db_manager.create_log("google_ads_credentials_error", {"error": error_msg})
            return {"success": False, "error": error_msg}
    
    async def test_google_ads_connection(self) -> Dict[str, Any]:
        """Тестирование подключения к Google Ads API"""
        try:
            credentials = await db_manager.get_oauth_credentials("google_ads")
            if not credentials:
                return {"success": False, "error": "Google Ads credentials не настроены"}
            
            creds_data = credentials.get("credentials", {})
            if not creds_data.get("access_token"):
                return {"success": False, "error": "Google Ads не авторизован. Выполните авторизацию."}
            
            # Здесь будет реальная интеграция с Google Ads API
            # Пока возвращаем успешный результат для настроенных credentials
            
            await db_manager.create_log("google_ads_connection_test", {"success": True})
            
            return {
                "success": True,
                "message": "Google Ads подключение успешно (тестовый режим)",
                "customer_id": creds_data.get("customer_id")
            }
            
        except Exception as e:
            error_msg = f"Google Ads connection error: {e}"
            logger.error(error_msg)
            await db_manager.create_log("google_ads_connection_error", {"error": error_msg})
            return {"success": False, "error": error_msg}

# Глобальный экземпляр менеджера интеграций
integration_manager = IntegrationManager()
