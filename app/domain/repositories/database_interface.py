from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from uuid import UUID
from datetime import datetime


class DatabaseInterface(ABC):
    """Абстрактный интерфейс для работы с базой данных"""
    
    # Tenant operations
    @abstractmethod
    def get_tenant(self, tenant_id: UUID) -> Optional[Dict[str, Any]]:
        pass
    
    @abstractmethod
    def get_tenants(self, skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
        pass
    
    @abstractmethod
    def create_tenant(self, tenant_data: Dict[str, Any]) -> Dict[str, Any]:
        pass
    
    # User operations
    @abstractmethod
    def get_user(self, user_id: UUID) -> Optional[Dict[str, Any]]:
        pass
    
    @abstractmethod
    def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        pass
    
    @abstractmethod
    def get_users(self, tenant_id: UUID, skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
        pass
    
    @abstractmethod
    def create_user(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        pass
    
    @abstractmethod
    def create_user_with_password(self, user_data: Dict[str, Any], password: str) -> Dict[str, Any]:
        pass
    
    @abstractmethod
    def update_user_verification(self, user_id: UUID, is_verified: bool, verification_token: Optional[str] = None) -> Optional[Dict[str, Any]]:
        pass
    
    @abstractmethod
    def get_user_by_verification_token(self, token: str) -> Optional[Dict[str, Any]]:
        pass
    
    # Client operations
    @abstractmethod
    def get_client(self, client_id: UUID) -> Optional[Dict[str, Any]]:
        pass
    
    @abstractmethod
    def get_clients(self, tenant_id: UUID, skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
        pass
    
    @abstractmethod
    def create_client(self, client_data: Dict[str, Any]) -> Dict[str, Any]:
        pass
    
    @abstractmethod
    def update_client(self, client_id: UUID, client_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        pass
    
    @abstractmethod
    def delete_client(self, client_id: UUID) -> bool:
        pass
    
    # Session operations
    @abstractmethod
    def get_session(self, session_id: UUID) -> Optional[Dict[str, Any]]:
        pass
    
    @abstractmethod
    def get_sessions(self, client_id: UUID, skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
        pass
    
    @abstractmethod
    def create_session(self, session_data: Dict[str, Any]) -> Dict[str, Any]:
        pass
    
    @abstractmethod
    def update_session(self, session_id: UUID, session_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        pass
    
    @abstractmethod
    def delete_session(self, session_id: UUID) -> bool:
        pass
    
    # Note operations
    @abstractmethod
    def get_note(self, note_id: UUID) -> Optional[Dict[str, Any]]:
        pass
    
    @abstractmethod
    def get_notes(self, session_id: Optional[UUID] = None, skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
        pass
    
    @abstractmethod
    def create_note(self, note_data: Dict[str, Any]) -> Dict[str, Any]:
        pass
    
    @abstractmethod
    def update_note(self, note_id: UUID, note_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        pass
    
    @abstractmethod
    def delete_note(self, note_id: UUID) -> bool:
        pass
    
    # Media operations
    @abstractmethod
    def get_media(self, media_id: UUID) -> Optional[Dict[str, Any]]:
        pass
    
    @abstractmethod
    def get_media_by_session(self, session_id: UUID, skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
        pass
    
    @abstractmethod
    def create_media(self, media_data: Dict[str, Any]) -> Dict[str, Any]:
        pass
    
    @abstractmethod
    def update_media(self, media_id: UUID, media_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        pass
    
    @abstractmethod
    def delete_media(self, media_id: UUID) -> bool:
        pass
    
    # AI Insight operations
    @abstractmethod
    def get_ai_insight(self, insight_id: UUID) -> Optional[Dict[str, Any]]:
        pass
    
    @abstractmethod
    def get_ai_insights_by_session(self, session_id: UUID, skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
        pass
    
    @abstractmethod
    def create_ai_insight(self, insight_data: Dict[str, Any]) -> Dict[str, Any]:
        pass
    
    @abstractmethod
    def update_ai_insight(self, insight_id: UUID, insight_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        pass
    
    @abstractmethod
    def delete_ai_insight(self, insight_id: UUID) -> bool:
        pass 
