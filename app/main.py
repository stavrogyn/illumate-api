from fastapi import FastAPI, Depends, HTTPException, status, Response, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID
from datetime import timedelta
from app.infrastructure.database import models, crud
from app.application import schemas
from app.domain.services import auth_service
from app.infrastructure.database.database import get_engine, get_db
from app.infrastructure.database.database_factory import DatabaseFactory
from app.domain.repositories.database_interface import DatabaseInterface
from app.infrastructure.external.email_service import email_service

# Create database tables
models.Base.metadata.create_all(bind=get_engine())

app = FastAPI(
    title="Therapy Management API",
    description="API для управления терапевтической практикой с поддержкой ИИ",
    version="1.0.0",
    openapi_tags=[
        {"name": "auth", "description": "Аутентификация и авторизация"},
        {"name": "tenants", "description": "Управление организациями"},
        {"name": "users", "description": "Управление пользователями"},
        {"name": "clients", "description": "Управление клиентами"},
        {"name": "sessions", "description": "Управление сессиями"},
        {"name": "notes", "description": "Управление заметками"},
        {"name": "media", "description": "Управление медиафайлами"},
        {"name": "ai-insights", "description": "ИИ-инсайты и аналитика"},
    ]
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer(auto_error=False)


def get_database(db_session: Session = Depends(get_db)) -> DatabaseInterface:
    """Dependency для получения базы данных (реальной или мок)"""
    return DatabaseFactory.create_database(db_session)


def get_token_from_cookie(request: Request) -> Optional[str]:
    """Получает токен из cookie"""
    return request.cookies.get("session_token")


def get_current_user(
    request: Request,
    bearer_token: Optional[str] = Depends(security),
    database: DatabaseInterface = Depends(get_database)
):
    """Получает текущего пользователя из токена (cookie или Bearer)"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    # Пробуем получить токен из cookie или Bearer
    token = None
    if bearer_token and bearer_token.credentials:
        token = bearer_token.credentials
    else:
        token = get_token_from_cookie(request)
    
    if not token:
        raise credentials_exception
    
    payload = auth_service.verify_token(token)
    if payload is None:
        raise credentials_exception
    
    user_id: str = payload.get("sub")
    if user_id is None:
        raise credentials_exception
    
    user = database.get_user(UUID(user_id))
    if user is None:
        raise credentials_exception
    
    return user


# Authentication endpoints
@app.post("/auth/register", response_model=schemas.AuthResponse, status_code=status.HTTP_201_CREATED, tags=["auth"])
def register(auth_data: schemas.AuthRegister, database: DatabaseInterface = Depends(get_database)):
    """Регистрирует нового пользователя"""
    # Проверяем, что email не занят
    existing_user = database.get_user_by_email(auth_data.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Создаем tenant
    tenant = database.create_tenant({"name": auth_data.tenant_name})
    
    # Создаем пользователя
    password_hash = auth_service.get_password_hash(auth_data.password)
    verification_token = auth_service.generate_verification_token()
    
    user_data = {
        "email": auth_data.email,
        "password_hash": password_hash,
        "tenant_id": tenant["id"],
        "role": auth_data.role,
        "locale": auth_data.locale,
        "is_verified": False,
        "verification_token": verification_token
    }
    
    user = database.create_user(user_data)
    
    # Отправляем email для подтверждения
    email_service.send_verification_email(auth_data.email, verification_token, auth_data.tenant_name)
    
    return schemas.AuthResponse(
        message="User registered successfully. Please check your email for verification.",
        user_id=user["id"],
        email=user["email"],
        role=user["role"],
        tenant_id=user["tenant_id"]
    )


@app.post("/auth/login", response_model=schemas.AuthResponse, tags=["auth"])
def login(auth_data: schemas.AuthLogin, response: Response, database: DatabaseInterface = Depends(get_database)):
    """Вход пользователя"""
    # Получаем пользователя
    user = database.get_user_by_email(auth_data.email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    # Проверяем пароль
    if not auth_service.verify_password(auth_data.password, user["password_hash"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    # Проверяем, что email подтвержден
    if not user["is_verified"]:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email not verified. Please check your email and verify your account."
        )
    
    # Создаем JWT токен
    access_token_expires = timedelta(minutes=auth_service.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth_service.create_access_token(
        data={"sub": str(user["id"])}, expires_delta=access_token_expires
    )
    
    # Устанавливаем http-only cookie
    response.set_cookie(
        key="session_token",
        value=access_token,
        httponly=True,
        secure=False,  # Set to True in production with HTTPS
        samesite="lax",
        max_age=1800  # 30 minutes
    )
    
    return schemas.AuthResponse(
        message="Login successful",
        user_id=user["id"],
        email=user["email"],
        role=user["role"],
        tenant_id=user["tenant_id"]
    )


@app.get("/auth/verify", tags=["auth"])
def verify_email(token: str, database: DatabaseInterface = Depends(get_database)):
    """Подтверждает email пользователя"""
    user = database.get_user_by_verification_token(token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired verification token"
        )
    
    # Обновляем статус пользователя
    database.update_user_verification(user["id"], True, None)
    
    # Отправляем приветственное письмо
    tenant = database.get_tenant(user["tenant_id"])
    if tenant:
        email_service.send_welcome_email(user["email"], tenant["name"])
    
    return {"message": "Email verified successfully"}


@app.post("/auth/resend-verification", tags=["auth"])
def resend_verification_email(
    request_data: schemas.ResendVerificationEmail, 
    database: DatabaseInterface = Depends(get_database)
):
    """Повторно отправляет письмо для подтверждения email"""
    # Проверяем, что пользователь существует
    user = database.get_user_by_email(request_data.email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Проверяем, что email еще не подтвержден
    if user["is_verified"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email is already verified"
        )
    
    # Генерируем новый verification token
    new_verification_token = auth_service.generate_verification_token()
    
    # Обновляем пользователя с новым токеном
    updated_user = database.update_user_verification(
        user["id"], 
        False, 
        new_verification_token
    )
    
    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update verification token"
        )
    
    # Отправляем новое письмо для подтверждения
    tenant = database.get_tenant(user["tenant_id"])
    tenant_name = tenant["name"] if tenant else "Our Service"
    
    email_sent = email_service.send_verification_email(
        request_data.email, 
        new_verification_token, 
        tenant_name
    )
    
    if not email_sent:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send verification email"
        )
    
    return {
        "message": "Verification email sent successfully",
        "email": request_data.email
    }


@app.post("/auth/logout", tags=["auth"])
def logout(response: Response):
    """Выход пользователя"""
    response.delete_cookie(key="session_token")
    return {"message": "Logged out successfully"}


@app.get("/auth/me", response_model=schemas.UserRead, tags=["auth"])
def get_current_user_info(current_user: dict = Depends(get_current_user)):
    """Получает информацию о текущем пользователе"""
    return current_user


@app.get("/")
def read_root():
    return {"message": "Welcome to Therapy Management API!"}


@app.get("/health")
def health_check():
    return {"status": "healthy"}


# Tenant endpoints
@app.post("/tenants/", response_model=schemas.TenantRead, status_code=status.HTTP_201_CREATED, tags=["tenants"])
def create_tenant(tenant: schemas.TenantCreate, db: Session = Depends(get_db)):
    return crud.create_tenant(db=db, tenant=tenant)


@app.get("/tenants/", response_model=List[schemas.TenantRead], tags=["tenants"])
def read_tenants(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    tenants = crud.get_tenants(db, skip=skip, limit=limit)
    return tenants


@app.get("/tenants/{tenant_id}", response_model=schemas.TenantRead, tags=["tenants"])
def read_tenant(tenant_id: UUID, db: Session = Depends(get_db)):
    db_tenant = crud.get_tenant(db, tenant_id=tenant_id)
    if db_tenant is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tenant not found"
        )
    return db_tenant


# User endpoints
@app.post("/users/", response_model=schemas.UserRead, status_code=status.HTTP_201_CREATED, tags=["users"])
def create_user(user: schemas.UserCreate, tenant_id: UUID, password: str, db: Session = Depends(get_db)):
    # Verify that the tenant exists
    db_tenant = crud.get_tenant(db, tenant_id=tenant_id)
    if not db_tenant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tenant not found"
        )
    
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    return crud.create_user_with_password(db=db, user=user, tenant_id=tenant_id, password=password)


@app.get("/users/", response_model=List[schemas.UserRead], tags=["users"])
def read_users(tenant_id: UUID, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    users = crud.get_users(db, tenant_id=tenant_id, skip=skip, limit=limit)
    return users


@app.get("/users/{user_id}", response_model=schemas.UserRead, tags=["users"])
def read_user(user_id: UUID, db: Session = Depends(get_db)):
    db_user = crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return db_user


# Client endpoints
@app.post("/clients/", response_model=schemas.ClientRead, status_code=status.HTTP_201_CREATED, tags=["clients"])
def create_client(client: schemas.ClientCreate, tenant_id: UUID, db: Session = Depends(get_db)):
    # Verify that the tenant exists
    db_tenant = crud.get_tenant(db, tenant_id=tenant_id)
    if not db_tenant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tenant not found"
        )
    
    return crud.create_client(db=db, client=client, tenant_id=tenant_id)


@app.get("/clients/", response_model=List[schemas.ClientRead], tags=["clients"])
def read_clients(tenant_id: UUID, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    clients = crud.get_clients(db, tenant_id=tenant_id, skip=skip, limit=limit)
    return clients


@app.get("/clients/{client_id}", response_model=schemas.ClientRead, tags=["clients"])
def read_client(client_id: UUID, db: Session = Depends(get_db)):
    db_client = crud.get_client(db, client_id=client_id)
    if db_client is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Client not found"
        )
    return db_client


@app.patch("/clients/{client_id}", response_model=schemas.ClientRead, tags=["clients"])
def update_client(client_id: UUID, client_update: schemas.ClientCreate, db: Session = Depends(get_db)):
    db_client = crud.update_client(db, client_id=client_id, client_update=client_update)
    if db_client is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Client not found"
        )
    return db_client


@app.delete("/clients/{client_id}", tags=["clients"])
def delete_client(client_id: UUID, db: Session = Depends(get_db)):
    success = crud.delete_client(db, client_id=client_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Client not found"
        )
    return {"message": "Client deleted successfully"}


# Session endpoints
@app.post("/sessions/", response_model=schemas.SessionRead, status_code=status.HTTP_201_CREATED, tags=["sessions"])
def create_session(session: schemas.SessionCreate, db: Session = Depends(get_db)):
    # Verify that the client exists
    db_client = crud.get_client(db, client_id=session.client_id)
    if not db_client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Client not found"
        )
    
    return crud.create_session(db=db, session=session)


@app.get("/sessions/", response_model=List[schemas.SessionRead], tags=["sessions"])
def read_sessions(client_id: UUID, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    sessions = crud.get_sessions(db, client_id=client_id, skip=skip, limit=limit)
    return sessions


@app.get("/sessions/{session_id}", response_model=schemas.SessionRead, tags=["sessions"])
def read_session(session_id: UUID, db: Session = Depends(get_db)):
    db_session = crud.get_session(db, session_id=session_id)
    if db_session is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )
    return db_session


@app.patch("/sessions/{session_id}", response_model=schemas.SessionRead, tags=["sessions"])
def update_session(session_id: UUID, session_update: schemas.SessionCreate, db: Session = Depends(get_db)):
    db_session = crud.update_session(db, session_id=session_id, session_update=session_update)
    if db_session is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )
    return db_session


@app.delete("/sessions/{session_id}", tags=["sessions"])
def delete_session(session_id: UUID, db: Session = Depends(get_db)):
    success = crud.delete_session(db, session_id=session_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )
    return {"message": "Session deleted successfully"}


# Note endpoints
@app.post("/notes/", response_model=schemas.NoteRead, status_code=status.HTTP_201_CREATED, tags=["notes"])
def create_note(note: schemas.NoteCreate, author_id: UUID, db: Session = Depends(get_db)):
    # Verify that the author exists
    db_user = crud.get_user(db, user_id=author_id)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Author not found"
        )
    
    # Verify that the session exists if provided
    if note.session_id:
        db_session = crud.get_session(db, session_id=note.session_id)
        if not db_session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Session not found"
            )
    
    return crud.create_note(db=db, note=note, author_id=author_id)


@app.get("/notes/", response_model=List[schemas.NoteRead], tags=["notes"])
def read_notes(session_id: UUID = None, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    notes = crud.get_notes(db, session_id=session_id, skip=skip, limit=limit)
    return notes


@app.get("/notes/{note_id}", response_model=schemas.NoteRead, tags=["notes"])
def read_note(note_id: UUID, db: Session = Depends(get_db)):
    db_note = crud.get_note(db, note_id=note_id)
    if db_note is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Note not found"
        )
    return db_note


@app.patch("/notes/{note_id}", response_model=schemas.NoteRead, tags=["notes"])
def update_note(note_id: UUID, note_update: schemas.NoteCreate, db: Session = Depends(get_db)):
    db_note = crud.update_note(db, note_id=note_id, note_update=note_update)
    if db_note is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Note not found"
        )
    return db_note


@app.delete("/notes/{note_id}", tags=["notes"])
def delete_note(note_id: UUID, db: Session = Depends(get_db)):
    success = crud.delete_note(db, note_id=note_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Note not found"
        )
    return {"message": "Note deleted successfully"}


# Media endpoints
@app.post("/media/", response_model=schemas.MediaRead, status_code=status.HTTP_201_CREATED, tags=["media"])
def create_media(media: schemas.MediaCreate, db: Session = Depends(get_db)):
    # Verify that the session exists
    db_session = crud.get_session(db, session_id=media.session_id)
    if not db_session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )
    
    return crud.create_media(db=db, media=media)


@app.get("/media/", response_model=List[schemas.MediaRead], tags=["media"])
def read_media_by_session(session_id: UUID, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    media = crud.get_media_by_session(db, session_id=session_id, skip=skip, limit=limit)
    return media


@app.get("/media/{media_id}", response_model=schemas.MediaRead, tags=["media"])
def read_media(media_id: UUID, db: Session = Depends(get_db)):
    db_media = crud.get_media(db, media_id=media_id)
    if db_media is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Media not found"
        )
    return db_media


@app.patch("/media/{media_id}", response_model=schemas.MediaRead, tags=["media"])
def update_media(media_id: UUID, media_update: schemas.MediaCreate, db: Session = Depends(get_db)):
    db_media = crud.update_media(db, media_id=media_id, media_update=media_update)
    if db_media is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Media not found"
        )
    return db_media


@app.delete("/media/{media_id}", tags=["media"])
def delete_media(media_id: UUID, db: Session = Depends(get_db)):
    success = crud.delete_media(db, media_id=media_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Media not found"
        )
    return {"message": "Media deleted successfully"}


# AIInsight endpoints
@app.post("/ai-insights/", response_model=schemas.AIInsightRead, status_code=status.HTTP_201_CREATED, tags=["ai-insights"])
def create_ai_insight(insight: schemas.AIInsightCreate, db: Session = Depends(get_db)):
    # Verify that the session exists
    db_session = crud.get_session(db, session_id=insight.session_id)
    if not db_session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )
    
    return crud.create_ai_insight(db=db, insight=insight)


@app.get("/ai-insights/", response_model=List[schemas.AIInsightRead], tags=["ai-insights"])
def read_ai_insights_by_session(session_id: UUID, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    insights = crud.get_ai_insights_by_session(db, session_id=session_id, skip=skip, limit=limit)
    return insights


@app.get("/ai-insights/{insight_id}", response_model=schemas.AIInsightRead, tags=["ai-insights"])
def read_ai_insight(insight_id: UUID, db: Session = Depends(get_db)):
    db_insight = crud.get_ai_insight(db, insight_id=insight_id)
    if db_insight is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="AI Insight not found"
        )
    return db_insight


@app.patch("/ai-insights/{insight_id}", response_model=schemas.AIInsightRead, tags=["ai-insights"])
def update_ai_insight(insight_id: UUID, insight_update: schemas.AIInsightCreate, db: Session = Depends(get_db)):
    db_insight = crud.update_ai_insight(db, insight_id=insight_id, insight_update=insight_update)
    if db_insight is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="AI Insight not found"
        )
    return db_insight


@app.delete("/ai-insights/{insight_id}", tags=["ai-insights"])
def delete_ai_insight(insight_id: UUID, db: Session = Depends(get_db)):
    success = crud.delete_ai_insight(db, insight_id=insight_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="AI Insight not found"
        )
    return {"message": "AI Insight deleted successfully"} 
