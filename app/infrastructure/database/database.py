from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from app.config import settings

# Create Base class
Base = declarative_base()

# Create SQLAlchemy engine (lazy initialization)
_engine = None
_SessionLocal = None

def get_engine():
    """Lazy initialization of SQLAlchemy engine"""
    global _engine
    if _engine is None:
        _engine = create_engine(settings.database_url)
    return _engine

def get_session_local():
    """Lazy initialization of SessionLocal"""
    global _SessionLocal
    if _SessionLocal is None:
        _SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=get_engine())
    return _SessionLocal

# Dependency to get database session
def get_db():
    SessionLocal = get_session_local()
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close() 
