from pydantic_settings import BaseSettings
from typing import Optional
import os

class Settings(BaseSettings):
    database_url: str = "postgresql://postgres:password@localhost:5432/fastapi_db"
    secret_key: str = "your-secret-key-here-change-in-production"
    debug: bool = True
    
    # AWS SES settings
    aws_region: Optional[str] = os.getenv("AWS_REGION")
    aws_access_key_id: Optional[str] = os.getenv("AWS_ACCESS_KEY_ID")
    aws_secret_access_key: Optional[str] = os.getenv("AWS_SECRET_ACCESS_KEY")
    sender_email: Optional[str] = os.getenv("SENDER_EMAIL")
    base_url: Optional[str] = os.getenv("BASE_URL")
    
    class Config:
        env_file = ".env"


settings = Settings() 
