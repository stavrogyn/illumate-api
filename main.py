from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
import models, schemas, crud
from database import engine, get_db

# Create database tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Therapy Management API",
    description="API для управления терапевтической практикой с поддержкой ИИ",
    version="1.0.0",
    openapi_tags=[
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
def create_user(user: schemas.UserCreate, tenant_id: UUID, db: Session = Depends(get_db)):
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
    
    return crud.create_user(db=db, user=user, tenant_id=tenant_id)


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
