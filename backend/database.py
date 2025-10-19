from supabase import create_client, Client
from typing import Optional, List, Dict, Any
import asyncio
from datetime import datetime
import uuid
from config import SUPABASE_URL, SUPABASE_KEY

class DatabaseManager:
    def __init__(self):
        self.supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    
    # ==================== MODAL IMAGES ====================
    
    async def create_modal_image(self, filename: str, file_path: str, file_size: int) -> Dict[str, Any]:
        """Создание записи модалки в БД"""
        modal_data = {
            "id": str(uuid.uuid4()),
            "filename": filename,
            "file_path": file_path,
            "file_size": file_size,
            "is_active": True,
            "created_at": datetime.now().isoformat()
        }
        
        result = self.supabase.table("modal_images").insert(modal_data).execute()
        return result.data[0] if result.data else None
    
    async def get_modal_images(self) -> List[Dict[str, Any]]:
        """Получение всех модалок"""
        result = self.supabase.table("modal_images").select("*").order("created_at", desc=True).execute()
        return result.data if result.data else []
    
    async def get_modal_image_by_id(self, modal_id: str) -> Optional[Dict[str, Any]]:
        """Получение модалки по ID"""
        result = self.supabase.table("modal_images").select("*").eq("id", modal_id).execute()
        return result.data[0] if result.data else None
    
    async def delete_modal_image(self, modal_id: str) -> bool:
        """Удаление модалки"""
        result = self.supabase.table("modal_images").delete().eq("id", modal_id).execute()
        return len(result.data) > 0
    
    # ==================== TEMPLATES ====================
    
    async def create_template(self, template_data: Dict[str, Any]) -> Dict[str, Any]:
        """Создание шаблона"""
        template_data.update({
            "id": str(uuid.uuid4()),
            "created_at": datetime.now().isoformat()
        })
        
        result = self.supabase.table("templates").insert(template_data).execute()
        return result.data[0] if result.data else None
    
    async def get_templates(self) -> List[Dict[str, Any]]:
        """Получение всех шаблонов"""
        result = self.supabase.table("templates").select("*").order("created_at", desc=True).execute()
        return result.data if result.data else []
    
    async def get_template_by_id(self, template_id: str) -> Optional[Dict[str, Any]]:
        """Получение шаблона по ID"""
        result = self.supabase.table("templates").select("*").eq("id", template_id).execute()
        return result.data[0] if result.data else None
    
    # ==================== UPLOADS ====================
    
    async def create_upload(self, upload_data: Dict[str, Any]) -> Dict[str, Any]:
        """Создание записи загрузки"""
        upload_data.update({
            "id": str(uuid.uuid4()),
            "upload_date": datetime.now().isoformat(),
            "status": upload_data.get("status", "active")
        })
        
        result = self.supabase.table("uploads").insert(upload_data).execute()
        return result.data[0] if result.data else None
    
    async def get_uploads(self) -> List[Dict[str, Any]]:
        """Получение всех загрузок"""
        result = self.supabase.table("uploads").select("*").order("upload_date", desc=True).execute()
        return result.data if result.data else []
    
    async def get_upload_by_id(self, upload_id: str) -> Optional[Dict[str, Any]]:
        """Получение загрузки по ID"""
        result = self.supabase.table("uploads").select("*").eq("id", upload_id).execute()
        return result.data[0] if result.data else None
    
    async def update_upload_status(self, upload_id: str, status: str) -> bool:
        """Обновление статуса загрузки"""
        result = self.supabase.table("uploads").update({
            "status": status,
            "updated_at": datetime.now().isoformat()
        }).eq("id", upload_id).execute()
        
        return len(result.data) > 0
    
    async def update_upload_performance(self, upload_id: str, performance_data: Dict[str, Any]) -> bool:
        """Обновление метрик загрузки"""
        result = self.supabase.table("uploads").update({
            "performance": performance_data,
            "updated_at": datetime.now().isoformat()
        }).eq("id", upload_id).execute()
        
        return len(result.data) > 0
    
    # ==================== USERS ====================
    
    async def create_user(self, email: str, role_id: str = None) -> Dict[str, Any]:
        """Создание пользователя"""
        user_data = {
            "id": str(uuid.uuid4()),
            "email": email,
            "role_id": role_id,
            "created_at": datetime.now().isoformat()
        }
        
        result = self.supabase.table("users").insert(user_data).execute()
        return result.data[0] if result.data else None
    
    async def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Получение пользователя по email"""
        result = self.supabase.table("users").select("*").eq("email", email).execute()
        return result.data[0] if result.data else None
    
    # ==================== ROLES ====================
    
    async def get_roles(self) -> List[Dict[str, Any]]:
        """Получение всех ролей"""
        result = self.supabase.table("roles").select("*").execute()
        return result.data if result.data else []
    
    async def create_default_roles(self):
        """Создание ролей по умолчанию"""
        default_roles = [
            {"id": str(uuid.uuid4()), "name": "admin", "description": "Администратор"},
            {"id": str(uuid.uuid4()), "name": "user", "description": "Обычный пользователь"},
            {"id": str(uuid.uuid4()), "name": "viewer", "description": "Только просмотр"}
        ]
        
        for role in default_roles:
            # Проверяем, существует ли роль
            existing = self.supabase.table("roles").select("*").eq("name", role["name"]).execute()
            if not existing.data:
                self.supabase.table("roles").insert(role).execute()
    
    # ==================== OAUTH CREDENTIALS ====================
    
    async def save_oauth_credentials(self, service: str, credentials: Dict[str, Any]) -> Dict[str, Any]:
        """Сохранение OAuth учетных данных (upsert)"""
        # Сначала проверим, есть ли уже запись для этого сервиса
        existing = await self.get_oauth_credentials(service)
        
        if existing:
            # Обновляем существующую запись
            credentials_data = {
                "credentials": credentials,
                "updated_at": datetime.now().isoformat()
            }
            result = self.supabase.table("oauth_credentials").update(credentials_data).eq("id", existing["id"]).execute()
        else:
            # Создаем новую запись
            credentials_data = {
                "id": str(uuid.uuid4()),
                "service": service,
                "credentials": credentials,
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat()
            }
            result = self.supabase.table("oauth_credentials").insert(credentials_data).execute()
        
        return result.data[0] if result.data else None
    
    async def get_oauth_credentials(self, service: str) -> Optional[Dict[str, Any]]:
        """Получение OAuth учетных данных"""
        result = self.supabase.table("oauth_credentials").select("*").eq("service", service).order("created_at", desc=True).limit(1).execute()
        return result.data[0] if result.data else None
    
    # ==================== LOGS ====================
    
    async def create_log(self, action: str, metadata: Dict[str, Any] = None, user_id: str = None) -> Dict[str, Any]:
        """Создание записи в логах"""
        log_data = {
            "id": str(uuid.uuid4()),
            "action": action,
            "metadata": metadata or {},
            "user_id": user_id,
            "created_at": datetime.now().isoformat()
        }
        
        result = self.supabase.table("logs").insert(log_data).execute()
        return result.data[0] if result.data else None

# Глобальный экземпляр менеджера БД
db_manager = DatabaseManager()
