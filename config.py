from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    database_url: str = "postgresql://postgres:password@localhost:5432/fastapi_db"
    secret_key: str = "your-secret-key-here-change-in-production"
    debug: bool = True
    
    class Config:
        env_file = ".env"


settings = Settings() 
