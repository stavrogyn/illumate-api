from datetime import datetime
from typing import List, Optional
from uuid import UUID
from pydantic import BaseModel, Field, EmailStr


# ----- Tenant -----
class TenantCreate(BaseModel):
    name: str = Field(max_length=120)


class TenantRead(BaseModel):
    id: UUID
    name: str
    plan: str
    created_at: datetime

    class Config:
        from_attributes = True


# ----- User -----
class UserCreate(BaseModel):
    email: EmailStr
    role: str = Field(example="therapist")
    locale: str = "en"


class UserRead(BaseModel):
    id: UUID
    email: EmailStr
    role: str
    locale: str
    created_at: datetime

    class Config:
        from_attributes = True


# ----- Client -----
class ClientCreate(BaseModel):
    full_name: str
    birthday: Optional[datetime] = None
    tags: List[str] = []


class ClientRead(BaseModel):
    id: UUID
    full_name: str
    birthday: Optional[datetime]
    tags: List[str]
    created_at: datetime

    class Config:
        from_attributes = True


# ----- Session -----
class SessionCreate(BaseModel):
    client_id: UUID
    scheduled_at: datetime
    duration_min: int = 50


class SessionRead(BaseModel):
    id: UUID
    client_id: UUID
    scheduled_at: datetime
    duration_min: int
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


# ----- Note -----
class NoteCreate(BaseModel):
    session_id: Optional[UUID] = None
    body_md: str


class NoteRead(BaseModel):
    id: UUID
    session_id: Optional[UUID]
    author_id: UUID
    body_md: str
    created_at: datetime

    class Config:
        from_attributes = True


# ----- Media -----
class MediaCreate(BaseModel):
    session_id: UUID
    type: str = Field(example="audio")
    url: str
    transcription: Optional[dict] = None


class MediaRead(BaseModel):
    id: UUID
    session_id: UUID
    type: str
    url: str
    transcription: Optional[dict]
    created_at: datetime

    class Config:
        from_attributes = True


# ----- AIInsight -----
class AIInsightCreate(BaseModel):
    session_id: UUID
    kind: str = Field(example="summary")
    content_json: dict
    embedding: Optional[List[float]] = None


class AIInsightRead(BaseModel):
    id: UUID
    session_id: UUID
    kind: str
    content_json: dict
    embedding: Optional[List[float]]
    created_at: datetime

    class Config:
        from_attributes = True 
