from typing import List, Optional, Dict, Any
from uuid import UUID, uuid4
from datetime import datetime, timezone
from app.domain.repositories.database_interface import DatabaseInterface


class MockDatabase(DatabaseInterface):
    """Мок-реализация базы данных для тестирования"""
    
    def __init__(self):
        self.tenants: Dict[UUID, Dict[str, Any]] = {}
        self.users: Dict[UUID, Dict[str, Any]] = {}
        self.clients: Dict[UUID, Dict[str, Any]] = {}
        self.sessions: Dict[UUID, Dict[str, Any]] = {}
        self.notes: Dict[UUID, Dict[str, Any]] = {}
        self.media: Dict[UUID, Dict[str, Any]] = {}
        self.ai_insights: Dict[UUID, Dict[str, Any]] = {}
        self.email_to_user: Dict[str, UUID] = {}
        self.verification_tokens: Dict[str, UUID] = {}
    
    def _convert_to_dict(self, obj: Any) -> Dict[str, Any]:
        """Конвертирует объект в словарь"""
        if isinstance(obj, dict):
            return obj.copy()
        elif hasattr(obj, '__dict__'):
            return obj.__dict__.copy()
        else:
            return str(obj)
    
    def _add_timestamps(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Добавляет временные метки"""
        now = datetime.now(timezone.utc)
        data['created_at'] = now
        data['updated_at'] = now
        return data
    
    # Tenant operations
    def get_tenant(self, tenant_id: UUID) -> Optional[Dict[str, Any]]:
        return self.tenants.get(tenant_id)
    
    def get_tenants(self, skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
        tenants_list = list(self.tenants.values())
        return tenants_list[skip:skip + limit]
    
    def create_tenant(self, tenant_data: Dict[str, Any]) -> Dict[str, Any]:
        tenant_id = uuid4()
        tenant = {
            'id': tenant_id,
            'name': tenant_data['name'],
            'plan': tenant_data.get('plan', 'free')
        }
        tenant = self._add_timestamps(tenant)
        self.tenants[tenant_id] = tenant
        return tenant
    
    # User operations
    def get_user(self, user_id: UUID) -> Optional[Dict[str, Any]]:
        return self.users.get(user_id)
    
    def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        user_id = self.email_to_user.get(email)
        if user_id:
            return self.users.get(user_id)
        return None
    
    def get_users(self, tenant_id: UUID, skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
        users_list = [user for user in self.users.values() if user['tenant_id'] == tenant_id]
        return users_list[skip:skip + limit]
    
    def create_user(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        user_id = uuid4()
        user = {
            'id': user_id,
            'email': user_data['email'],
            'role': user_data['role'],
            'locale': user_data.get('locale', 'en'),
            'tenant_id': user_data['tenant_id'],
            'password_hash': user_data.get('password_hash', ''),
            'is_verified': user_data.get('is_verified', False),
            'verification_token': user_data.get('verification_token')
        }
        user = self._add_timestamps(user)
        self.users[user_id] = user
        self.email_to_user[user['email']] = user_id
        if user['verification_token']:
            self.verification_tokens[user['verification_token']] = user_id
        return user
    
    def create_user_with_password(self, user_data: Dict[str, Any], password: str) -> Dict[str, Any]:
        user_data['password_hash'] = f"hashed_{password}"  # Упрощенное хеширование для мока
        user_data['is_verified'] = True
        return self.create_user(user_data)
    
    def update_user_verification(self, user_id: UUID, is_verified: bool, verification_token: Optional[str] = None) -> Optional[Dict[str, Any]]:
        user = self.users.get(user_id)
        if not user:
            return None
        
        user['is_verified'] = is_verified
        if verification_token is not None:
            user['verification_token'] = verification_token
            if verification_token:
                self.verification_tokens[verification_token] = user_id
            else:
                # Удаляем старый токен
                old_token = user.get('verification_token')
                if old_token and old_token in self.verification_tokens:
                    del self.verification_tokens[old_token]
        
        user['updated_at'] = datetime.now(timezone.utc)
        return user
    
    def get_user_by_verification_token(self, token: str) -> Optional[Dict[str, Any]]:
        user_id = self.verification_tokens.get(token)
        if user_id:
            return self.users.get(user_id)
        return None
    
    # Client operations
    def get_client(self, client_id: UUID) -> Optional[Dict[str, Any]]:
        return self.clients.get(client_id)
    
    def get_clients(self, tenant_id: UUID, skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
        clients_list = [client for client in self.clients.values() if client['tenant_id'] == tenant_id]
        return clients_list[skip:skip + limit]
    
    def create_client(self, client_data: Dict[str, Any]) -> Dict[str, Any]:
        client_id = uuid4()
        client = {
            'id': client_id,
            'full_name': client_data['full_name'],
            'birthday': client_data.get('birthday'),
            'tags': client_data.get('tags', []),
            'tenant_id': client_data['tenant_id']
        }
        client = self._add_timestamps(client)
        self.clients[client_id] = client
        return client
    
    def update_client(self, client_id: UUID, client_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        client = self.clients.get(client_id)
        if not client:
            return None
        
        for key, value in client_data.items():
            if key in ['full_name', 'birthday', 'tags']:
                client[key] = value
        
        client['updated_at'] = datetime.now(timezone.utc)
        return client
    
    def delete_client(self, client_id: UUID) -> bool:
        if client_id in self.clients:
            del self.clients[client_id]
            return True
        return False
    
    # Session operations
    def get_session(self, session_id: UUID) -> Optional[Dict[str, Any]]:
        return self.sessions.get(session_id)
    
    def get_sessions(self, client_id: UUID, skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
        sessions_list = [session for session in self.sessions.values() if session['client_id'] == client_id]
        return sessions_list[skip:skip + limit]
    
    def create_session(self, session_data: Dict[str, Any]) -> Dict[str, Any]:
        session_id = uuid4()
        session = {
            'id': session_id,
            'client_id': session_data['client_id'],
            'scheduled_at': session_data['scheduled_at'],
            'duration_min': session_data.get('duration_min', 50),
            'status': session_data.get('status', 'planned')
        }
        session = self._add_timestamps(session)
        self.sessions[session_id] = session
        return session
    
    def update_session(self, session_id: UUID, session_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        session = self.sessions.get(session_id)
        if not session:
            return None
        
        for key, value in session_data.items():
            if key in ['client_id', 'scheduled_at', 'duration_min', 'status']:
                session[key] = value
        
        session['updated_at'] = datetime.now(timezone.utc)
        return session
    
    def delete_session(self, session_id: UUID) -> bool:
        if session_id in self.sessions:
            del self.sessions[session_id]
            return True
        return False
    
    # Note operations
    def get_note(self, note_id: UUID) -> Optional[Dict[str, Any]]:
        return self.notes.get(note_id)
    
    def get_notes(self, session_id: Optional[UUID] = None, skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
        notes_list = list(self.notes.values())
        if session_id:
            notes_list = [note for note in notes_list if note['session_id'] == session_id]
        return notes_list[skip:skip + limit]
    
    def create_note(self, note_data: Dict[str, Any]) -> Dict[str, Any]:
        note_id = uuid4()
        note = {
            'id': note_id,
            'session_id': note_data.get('session_id'),
            'author_id': note_data['author_id'],
            'body_md': note_data['body_md']
        }
        note = self._add_timestamps(note)
        self.notes[note_id] = note
        return note
    
    def update_note(self, note_id: UUID, note_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        note = self.notes.get(note_id)
        if not note:
            return None
        
        for key, value in note_data.items():
            if key in ['session_id', 'body_md']:
                note[key] = value
        
        note['updated_at'] = datetime.now(timezone.utc)
        return note
    
    def delete_note(self, note_id: UUID) -> bool:
        if note_id in self.notes:
            del self.notes[note_id]
            return True
        return False
    
    # Media operations
    def get_media(self, media_id: UUID) -> Optional[Dict[str, Any]]:
        return self.media.get(media_id)
    
    def get_media_by_session(self, session_id: UUID, skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
        media_list = [media for media in self.media.values() if media['session_id'] == session_id]
        return media_list[skip:skip + limit]
    
    def create_media(self, media_data: Dict[str, Any]) -> Dict[str, Any]:
        media_id = uuid4()
        media = {
            'id': media_id,
            'session_id': media_data['session_id'],
            'type': media_data['type'],
            'url': media_data['url'],
            'transcription': media_data.get('transcription')
        }
        media = self._add_timestamps(media)
        self.media[media_id] = media
        return media
    
    def update_media(self, media_id: UUID, media_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        media = self.media.get(media_id)
        if not media:
            return None
        
        for key, value in media_data.items():
            if key in ['session_id', 'type', 'url', 'transcription']:
                media[key] = value
        
        media['updated_at'] = datetime.now(timezone.utc)
        return media
    
    def delete_media(self, media_id: UUID) -> bool:
        if media_id in self.media:
            del self.media[media_id]
            return True
        return False
    
    # AI Insight operations
    def get_ai_insight(self, insight_id: UUID) -> Optional[Dict[str, Any]]:
        return self.ai_insights.get(insight_id)
    
    def get_ai_insights_by_session(self, session_id: UUID, skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
        insights_list = [insight for insight in self.ai_insights.values() if insight['session_id'] == session_id]
        return insights_list[skip:skip + limit]
    
    def create_ai_insight(self, insight_data: Dict[str, Any]) -> Dict[str, Any]:
        insight_id = uuid4()
        insight = {
            'id': insight_id,
            'session_id': insight_data['session_id'],
            'kind': insight_data['kind'],
            'content_json': insight_data['content_json'],
            'embedding': insight_data.get('embedding')
        }
        insight = self._add_timestamps(insight)
        self.ai_insights[insight_id] = insight
        return insight
    
    def update_ai_insight(self, insight_id: UUID, insight_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        insight = self.ai_insights.get(insight_id)
        if not insight:
            return None
        
        for key, value in insight_data.items():
            if key in ['session_id', 'kind', 'content_json', 'embedding']:
                insight[key] = value
        
        insight['updated_at'] = datetime.now(timezone.utc)
        return insight
    
    def delete_ai_insight(self, insight_id: UUID) -> bool:
        if insight_id in self.ai_insights:
            del self.ai_insights[insight_id]
            return True
        return False
    
    def clear(self):
        """Очищает все данные в мок-базе"""
        self.tenants.clear()
        self.users.clear()
        self.clients.clear()
        self.sessions.clear()
        self.notes.clear()
        self.media.clear()
        self.ai_insights.clear()
        self.email_to_user.clear()
        self.verification_tokens.clear() 
