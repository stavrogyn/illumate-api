from typing import List, Optional, Dict, Any
from uuid import UUID
from sqlalchemy.orm import Session
from app.domain.repositories.database_interface import DatabaseInterface
from app.infrastructure.database import models
from app.application import schemas
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class RealDatabase(DatabaseInterface):
    """Адаптер для реальной базы данных PostgreSQL"""
    
    def __init__(self, db_session: Session):
        self.db = db_session
    
    def _model_to_dict(self, model_instance) -> Dict[str, Any]:
        """Конвертирует SQLAlchemy модель в словарь"""
        if not model_instance:
            return None
        
        result = {}
        for column in model_instance.__table__.columns:
            value = getattr(model_instance, column.name)
            result[column.name] = value
        
        return result
    
    def _dict_to_model(self, model_class, data: Dict[str, Any]):
        """Конвертирует словарь в SQLAlchemy модель"""
        return model_class(**data)
    
    # Tenant operations
    def get_tenant(self, tenant_id: UUID) -> Optional[Dict[str, Any]]:
        tenant = self.db.query(models.Tenant).filter(models.Tenant.id == tenant_id).first()
        return self._model_to_dict(tenant)
    
    def get_tenants(self, skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
        tenants = self.db.query(models.Tenant).offset(skip).limit(limit).all()
        return [self._model_to_dict(tenant) for tenant in tenants]
    
    def create_tenant(self, tenant_data: Dict[str, Any]) -> Dict[str, Any]:
        tenant = models.Tenant(**tenant_data)
        self.db.add(tenant)
        self.db.commit()
        self.db.refresh(tenant)
        return self._model_to_dict(tenant)
    
    # User operations
    def get_user(self, user_id: UUID) -> Optional[Dict[str, Any]]:
        user = self.db.query(models.User).filter(models.User.id == user_id).first()
        return self._model_to_dict(user)
    
    def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        user = self.db.query(models.User).filter(models.User.email == email).first()
        return self._model_to_dict(user)
    
    def get_users(self, tenant_id: UUID, skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
        users = self.db.query(models.User).filter(models.User.tenant_id == tenant_id).offset(skip).limit(limit).all()
        return [self._model_to_dict(user) for user in users]
    
    def create_user(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        user = models.User(**user_data)
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return self._model_to_dict(user)
    
    def create_user_with_password(self, user_data: Dict[str, Any], password: str) -> Dict[str, Any]:
        password_hash = pwd_context.hash(password)
        user_data['password_hash'] = password_hash
        user_data['is_verified'] = True
        return self.create_user(user_data)
    
    def update_user_verification(self, user_id: UUID, is_verified: bool, verification_token: Optional[str] = None) -> Optional[Dict[str, Any]]:
        user = self.db.query(models.User).filter(models.User.id == user_id).first()
        if not user:
            return None
        
        user.is_verified = is_verified
        if verification_token is not None:
            user.verification_token = verification_token
        
        self.db.commit()
        self.db.refresh(user)
        return self._model_to_dict(user)
    
    def get_user_by_verification_token(self, token: str) -> Optional[Dict[str, Any]]:
        user = self.db.query(models.User).filter(models.User.verification_token == token).first()
        return self._model_to_dict(user)
    
    # Client operations
    def get_client(self, client_id: UUID) -> Optional[Dict[str, Any]]:
        client = self.db.query(models.Client).filter(models.Client.id == client_id).first()
        return self._model_to_dict(client)
    
    def get_clients(self, tenant_id: UUID, skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
        clients = self.db.query(models.Client).filter(models.Client.tenant_id == tenant_id).offset(skip).limit(limit).all()
        return [self._model_to_dict(client) for client in clients]
    
    def create_client(self, client_data: Dict[str, Any]) -> Dict[str, Any]:
        client = models.Client(**client_data)
        self.db.add(client)
        self.db.commit()
        self.db.refresh(client)
        return self._model_to_dict(client)
    
    def update_client(self, client_id: UUID, client_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        client = self.db.query(models.Client).filter(models.Client.id == client_id).first()
        if not client:
            return None
        
        for key, value in client_data.items():
            if hasattr(client, key):
                setattr(client, key, value)
        
        self.db.commit()
        self.db.refresh(client)
        return self._model_to_dict(client)
    
    def delete_client(self, client_id: UUID) -> bool:
        client = self.db.query(models.Client).filter(models.Client.id == client_id).first()
        if not client:
            return False
        
        self.db.delete(client)
        self.db.commit()
        return True
    
    # Session operations
    def get_session(self, session_id: UUID) -> Optional[Dict[str, Any]]:
        session = self.db.query(models.Session).filter(models.Session.id == session_id).first()
        return self._model_to_dict(session)
    
    def get_sessions(self, client_id: UUID, skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
        sessions = self.db.query(models.Session).filter(models.Session.client_id == client_id).offset(skip).limit(limit).all()
        return [self._model_to_dict(session) for session in sessions]
    
    def create_session(self, session_data: Dict[str, Any]) -> Dict[str, Any]:
        session = models.Session(**session_data)
        self.db.add(session)
        self.db.commit()
        self.db.refresh(session)
        return self._model_to_dict(session)
    
    def update_session(self, session_id: UUID, session_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        session = self.db.query(models.Session).filter(models.Session.id == session_id).first()
        if not session:
            return None
        
        for key, value in session_data.items():
            if hasattr(session, key):
                setattr(session, key, value)
        
        self.db.commit()
        self.db.refresh(session)
        return self._model_to_dict(session)
    
    def delete_session(self, session_id: UUID) -> bool:
        session = self.db.query(models.Session).filter(models.Session.id == session_id).first()
        if not session:
            return False
        
        self.db.delete(session)
        self.db.commit()
        return True
    
    # Note operations
    def get_note(self, note_id: UUID) -> Optional[Dict[str, Any]]:
        note = self.db.query(models.Note).filter(models.Note.id == note_id).first()
        return self._model_to_dict(note)
    
    def get_notes(self, session_id: Optional[UUID] = None, skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
        query = self.db.query(models.Note)
        if session_id:
            query = query.filter(models.Note.session_id == session_id)
        notes = query.offset(skip).limit(limit).all()
        return [self._model_to_dict(note) for note in notes]
    
    def create_note(self, note_data: Dict[str, Any]) -> Dict[str, Any]:
        note = models.Note(**note_data)
        self.db.add(note)
        self.db.commit()
        self.db.refresh(note)
        return self._model_to_dict(note)
    
    def update_note(self, note_id: UUID, note_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        note = self.db.query(models.Note).filter(models.Note.id == note_id).first()
        if not note:
            return None
        
        for key, value in note_data.items():
            if hasattr(note, key):
                setattr(note, key, value)
        
        self.db.commit()
        self.db.refresh(note)
        return self._model_to_dict(note)
    
    def delete_note(self, note_id: UUID) -> bool:
        note = self.db.query(models.Note).filter(models.Note.id == note_id).first()
        if not note:
            return False
        
        self.db.delete(note)
        self.db.commit()
        return True
    
    # Media operations
    def get_media(self, media_id: UUID) -> Optional[Dict[str, Any]]:
        media = self.db.query(models.Media).filter(models.Media.id == media_id).first()
        return self._model_to_dict(media)
    
    def get_media_by_session(self, session_id: UUID, skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
        media_list = self.db.query(models.Media).filter(models.Media.session_id == session_id).offset(skip).limit(limit).all()
        return [self._model_to_dict(media) for media in media_list]
    
    def create_media(self, media_data: Dict[str, Any]) -> Dict[str, Any]:
        media = models.Media(**media_data)
        self.db.add(media)
        self.db.commit()
        self.db.refresh(media)
        return self._model_to_dict(media)
    
    def update_media(self, media_id: UUID, media_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        media = self.db.query(models.Media).filter(models.Media.id == media_id).first()
        if not media:
            return None
        
        for key, value in media_data.items():
            if hasattr(media, key):
                setattr(media, key, value)
        
        self.db.commit()
        self.db.refresh(media)
        return self._model_to_dict(media)
    
    def delete_media(self, media_id: UUID) -> bool:
        media = self.db.query(models.Media).filter(models.Media.id == media_id).first()
        if not media:
            return False
        
        self.db.delete(media)
        self.db.commit()
        return True
    
    # AI Insight operations
    def get_ai_insight(self, insight_id: UUID) -> Optional[Dict[str, Any]]:
        insight = self.db.query(models.AIInsight).filter(models.AIInsight.id == insight_id).first()
        return self._model_to_dict(insight)
    
    def get_ai_insights_by_session(self, session_id: UUID, skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
        insights = self.db.query(models.AIInsight).filter(models.AIInsight.session_id == session_id).offset(skip).limit(limit).all()
        return [self._model_to_dict(insight) for insight in insights]
    
    def create_ai_insight(self, insight_data: Dict[str, Any]) -> Dict[str, Any]:
        insight = models.AIInsight(**insight_data)
        self.db.add(insight)
        self.db.commit()
        self.db.refresh(insight)
        return self._model_to_dict(insight)
    
    def update_ai_insight(self, insight_id: UUID, insight_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        insight = self.db.query(models.AIInsight).filter(models.AIInsight.id == insight_id).first()
        if not insight:
            return None
        
        for key, value in insight_data.items():
            if hasattr(insight, key):
                setattr(insight, key, value)
        
        self.db.commit()
        self.db.refresh(insight)
        return self._model_to_dict(insight)
    
    def delete_ai_insight(self, insight_id: UUID) -> bool:
        insight = self.db.query(models.AIInsight).filter(models.AIInsight.id == insight_id).first()
        if not insight:
            return False
        
        self.db.delete(insight)
        self.db.commit()
        return True 
