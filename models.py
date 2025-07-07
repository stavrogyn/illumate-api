from datetime import datetime
from uuid import uuid4
from sqlalchemy import (
    Column, String, DateTime, Enum, ForeignKey, Integer,
    Boolean, JSON, UniqueConstraint, ARRAY
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import declarative_base, relationship
from pgvector.sqlalchemy import Vector
from database import Base


class TimestampMixin:
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime,
                        default=datetime.utcnow,
                        onupdate=datetime.utcnow,
                        nullable=False)


class Tenant(Base, TimestampMixin):
    __tablename__ = "tenants"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    name = Column(String(120), nullable=False, unique=True)
    plan = Column(Enum("free", "pro", "org", name="plan_t"), default="free")


class User(Base, TimestampMixin):
    __tablename__ = "users"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    tenant_id = Column(ForeignKey("tenants.id"), nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    role = Column(Enum("therapist", "assistant", "owner", name="user_role"), nullable=False)
    locale = Column(String(8), default="en")
    is_verified = Column(Boolean, default=False, nullable=False)
    verification_token = Column(String, unique=True, nullable=True)
    tenant = relationship("Tenant", back_populates="users")


Tenant.users = relationship("User", back_populates="tenant", cascade="all, delete")


class Client(Base, TimestampMixin):
    __tablename__ = "clients"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    tenant_id = Column(ForeignKey("tenants.id"), nullable=False)
    full_name = Column(String(120), nullable=False)
    birthday = Column(DateTime)
    tags = Column(ARRAY(String))  # PostgreSQL array
    tenant = relationship("Tenant")


class ClientUser(Base):
    __tablename__ = "clients_users"
    user_id = Column(ForeignKey("users.id"), primary_key=True)
    client_id = Column(ForeignKey("clients.id"), primary_key=True)
    role = Column(Enum("primary", "viewer", name="client_user_role"), default="primary")


class Session(Base, TimestampMixin):
    __tablename__ = "sessions"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    client_id = Column(ForeignKey("clients.id"), nullable=False)
    scheduled_at = Column(DateTime, nullable=False)
    duration_min = Column(Integer)
    status = Column(Enum("planned", "in_progress", "done", name="session_status"), default="planned")
    client = relationship("Client")


class Note(Base, TimestampMixin):
    __tablename__ = "notes"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    session_id = Column(ForeignKey("sessions.id"), nullable=True)
    author_id = Column(ForeignKey("users.id"), nullable=False)
    body_md = Column(String)
    author = relationship("User")


class Media(Base, TimestampMixin):
    __tablename__ = "media"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    session_id = Column(ForeignKey("sessions.id"), nullable=False)
    type = Column(Enum("audio", "video", "image", name="media_type"))
    url = Column(String, nullable=False)
    transcription = Column(JSON)


class AIInsight(Base, TimestampMixin):
    __tablename__ = "ai_insights"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    session_id = Column(ForeignKey("sessions.id"), nullable=False)
    kind = Column(Enum("summary", "trigger", "todo", name="insight_kind"))
    content_json = Column(JSON, nullable=False)
    embedding = Column(Vector(1536))  # pgvector 
