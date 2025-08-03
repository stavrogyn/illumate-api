from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import List, Optional
from uuid import UUID
from app.infrastructure.database import models
from app.application import schemas
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


# Tenant CRUD operations
def get_tenant(db: Session, tenant_id: UUID) -> Optional[models.Tenant]:
    return db.query(models.Tenant).filter(models.Tenant.id == tenant_id).first()


def get_tenants(db: Session, skip: int = 0, limit: int = 100) -> List[models.Tenant]:
    return db.query(models.Tenant).offset(skip).limit(limit).all()


def create_tenant(db: Session, tenant: schemas.TenantCreate) -> models.Tenant:
    db_tenant = models.Tenant(**tenant.dict())
    db.add(db_tenant)
    db.commit()
    db.refresh(db_tenant)
    return db_tenant


# User CRUD operations
def get_user(db: Session, user_id: UUID) -> Optional[models.User]:
    return db.query(models.User).filter(models.User.id == user_id).first()


def get_user_by_email(db: Session, email: str) -> Optional[models.User]:
    return db.query(models.User).filter(models.User.email == email).first()


def get_users(db: Session, tenant_id: UUID, skip: int = 0, limit: int = 100) -> List[models.User]:
    return db.query(models.User).filter(models.User.tenant_id == tenant_id).offset(skip).limit(limit).all()


def create_user(db: Session, user: schemas.UserCreate, tenant_id: UUID) -> models.User:
    db_user = models.User(**user.dict(), tenant_id=tenant_id)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def create_user_with_password(db: Session, user: schemas.UserCreate, tenant_id: UUID, password: str) -> models.User:
    """Создает пользователя с хешированным паролем"""
    password_hash = get_password_hash(password)
    db_user = models.User(
        **user.dict(),
        tenant_id=tenant_id,
        password_hash=password_hash,
        is_verified=True  # Администратор создает пользователя как подтвержденного
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def delete_user(db: Session, user_id: int) -> bool:
    db_user = get_user(db, user_id)
    if not db_user:
        return False
    
    db.delete(db_user)
    db.commit()
    return True


# Client CRUD operations
def get_client(db: Session, client_id: UUID) -> Optional[models.Client]:
    return db.query(models.Client).filter(models.Client.id == client_id).first()


def get_clients(db: Session, tenant_id: UUID, skip: int = 0, limit: int = 100) -> List[models.Client]:
    return db.query(models.Client).filter(models.Client.tenant_id == tenant_id).offset(skip).limit(limit).all()


def create_client(db: Session, client: schemas.ClientCreate, tenant_id: UUID) -> models.Client:
    db_client = models.Client(**client.dict(), tenant_id=tenant_id)
    db.add(db_client)
    db.commit()
    db.refresh(db_client)
    return db_client


def update_client(db: Session, client_id: UUID, client_update: schemas.ClientCreate) -> Optional[models.Client]:
    db_client = get_client(db, client_id)
    if not db_client:
        return None
    
    update_data = client_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_client, field, value)
    
    db.commit()
    db.refresh(db_client)
    return db_client


def delete_client(db: Session, client_id: UUID) -> bool:
    db_client = get_client(db, client_id)
    if not db_client:
        return False
    
    db.delete(db_client)
    db.commit()
    return True


# Session CRUD operations
def get_session(db: Session, session_id: UUID) -> Optional[models.Session]:
    return db.query(models.Session).filter(models.Session.id == session_id).first()


def get_sessions(db: Session, client_id: UUID, skip: int = 0, limit: int = 100) -> List[models.Session]:
    return db.query(models.Session).filter(models.Session.client_id == client_id).offset(skip).limit(limit).all()


def create_session(db: Session, session: schemas.SessionCreate) -> models.Session:
    db_session = models.Session(**session.dict())
    db.add(db_session)
    db.commit()
    db.refresh(db_session)
    return db_session


def update_session(db: Session, session_id: UUID, session_update: schemas.SessionCreate) -> Optional[models.Session]:
    db_session = get_session(db, session_id)
    if not db_session:
        return None
    
    update_data = session_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_session, field, value)
    
    db.commit()
    db.refresh(db_session)
    return db_session


def delete_session(db: Session, session_id: UUID) -> bool:
    db_session = get_session(db, session_id)
    if not db_session:
        return False
    
    db.delete(db_session)
    db.commit()
    return True


# Note CRUD operations
def get_note(db: Session, note_id: UUID) -> Optional[models.Note]:
    return db.query(models.Note).filter(models.Note.id == note_id).first()


def get_notes(db: Session, session_id: Optional[UUID] = None, skip: int = 0, limit: int = 100) -> List[models.Note]:
    query = db.query(models.Note)
    if session_id:
        query = query.filter(models.Note.session_id == session_id)
    return query.offset(skip).limit(limit).all()


def create_note(db: Session, note: schemas.NoteCreate, author_id: UUID) -> models.Note:
    db_note = models.Note(**note.dict(), author_id=author_id)
    db.add(db_note)
    db.commit()
    db.refresh(db_note)
    return db_note


def update_note(db: Session, note_id: UUID, note_update: schemas.NoteCreate) -> Optional[models.Note]:
    db_note = get_note(db, note_id)
    if not db_note:
        return None
    
    update_data = note_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_note, field, value)
    
    db.commit()
    db.refresh(db_note)
    return db_note


def delete_note(db: Session, note_id: UUID) -> bool:
    db_note = get_note(db, note_id)
    if not db_note:
        return False
    
    db.delete(db_note)
    db.commit()
    return True


# Media CRUD operations
def get_media(db: Session, media_id: UUID) -> Optional[models.Media]:
    return db.query(models.Media).filter(models.Media.id == media_id).first()


def get_media_by_session(db: Session, session_id: UUID, skip: int = 0, limit: int = 100) -> List[models.Media]:
    return db.query(models.Media).filter(models.Media.session_id == session_id).offset(skip).limit(limit).all()


def create_media(db: Session, media: schemas.MediaCreate) -> models.Media:
    db_media = models.Media(**media.dict())
    db.add(db_media)
    db.commit()
    db.refresh(db_media)
    return db_media


def update_media(db: Session, media_id: UUID, media_update: schemas.MediaCreate) -> Optional[models.Media]:
    db_media = get_media(db, media_id)
    if not db_media:
        return None
    
    update_data = media_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_media, field, value)
    
    db.commit()
    db.refresh(db_media)
    return db_media


def delete_media(db: Session, media_id: UUID) -> bool:
    db_media = get_media(db, media_id)
    if not db_media:
        return False
    
    db.delete(db_media)
    db.commit()
    return True


# AIInsight CRUD operations
def get_ai_insight(db: Session, insight_id: UUID) -> Optional[models.AIInsight]:
    return db.query(models.AIInsight).filter(models.AIInsight.id == insight_id).first()


def get_ai_insights_by_session(db: Session, session_id: UUID, skip: int = 0, limit: int = 100) -> List[models.AIInsight]:
    return db.query(models.AIInsight).filter(models.AIInsight.session_id == session_id).offset(skip).limit(limit).all()


def create_ai_insight(db: Session, insight: schemas.AIInsightCreate) -> models.AIInsight:
    db_insight = models.AIInsight(**insight.dict())
    db.add(db_insight)
    db.commit()
    db.refresh(db_insight)
    return db_insight


def update_ai_insight(db: Session, insight_id: UUID, insight_update: schemas.AIInsightCreate) -> Optional[models.AIInsight]:
    db_insight = get_ai_insight(db, insight_id)
    if not db_insight:
        return None
    
    update_data = insight_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_insight, field, value)
    
    db.commit()
    db.refresh(db_insight)
    return db_insight


def delete_ai_insight(db: Session, insight_id: UUID) -> bool:
    db_insight = get_ai_insight(db, insight_id)
    if not db_insight:
        return False
    
    db.delete(db_insight)
    db.commit()
    return True 
