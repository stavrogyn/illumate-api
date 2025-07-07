import os
import secrets
import smtplib
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional
from uuid import UUID
from passlib.context import CryptContext
from jose import JWTError, jwt
from sqlalchemy.orm import Session
import models
import crud
import schemas

# Настройки безопасности
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Настройки для хеширования паролей
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Настройки для отправки email
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USERNAME = os.getenv("SMTP_USERNAME", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
FROM_EMAIL = os.getenv("FROM_EMAIL", "noreply@therapyapp.com")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Проверяет пароль"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Хеширует пароль"""
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Создает JWT токен"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_token(token: str) -> Optional[dict]:
    """Проверяет JWT токен"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None


def generate_verification_token() -> str:
    """Генерирует токен для подтверждения email"""
    return secrets.token_urlsafe(32)


def send_verification_email(email: str, token: str, tenant_name: str):
    """Отправляет email для подтверждения"""
    if not SMTP_USERNAME or not SMTP_PASSWORD:
        print(f"Email verification would be sent to {email} with token: {token}")
        return
    
    try:
        msg = MIMEMultipart()
        msg['From'] = FROM_EMAIL
        msg['To'] = email
        msg['Subject'] = f"Подтверждение регистрации в {tenant_name}"
        
        body = f"""
        Здравствуйте!
        
        Спасибо за регистрацию в {tenant_name}. Для подтверждения вашего email перейдите по ссылке:
        
        http://localhost:8000/auth/verify?token={token}
        
        Если вы не регистрировались в нашем сервисе, проигнорируйте это письмо.
        
        С уважением,
        Команда {tenant_name}
        """
        
        msg.attach(MIMEText(body, 'plain', 'utf-8'))
        
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SMTP_USERNAME, SMTP_PASSWORD)
        text = msg.as_string()
        server.sendmail(FROM_EMAIL, email, text)
        server.quit()
        
    except Exception as e:
        print(f"Error sending email: {e}")


def authenticate_user(db: Session, email: str, password: str) -> Optional[models.User]:
    """Аутентифицирует пользователя"""
    user = crud.get_user_by_email(db, email=email)
    if not user:
        return None
    if not verify_password(password, user.password_hash):
        return None
    return user


def register_user(db: Session, email: str, password: str, tenant_name: str, role: str, locale: str = "en") -> models.User:
    """Регистрирует нового пользователя"""
    # Создаем tenant
    tenant = crud.create_tenant(db, schemas.TenantCreate(name=tenant_name))
    
    # Создаем пользователя
    password_hash = get_password_hash(password)
    verification_token = generate_verification_token()
    
    user = models.User(
        email=email,
        password_hash=password_hash,
        tenant_id=tenant.id,
        role=role,
        locale=locale,
        is_verified=False,
        verification_token=verification_token
    )
    
    db.add(user)
    db.commit()
    db.refresh(user)
    
    # Отправляем email для подтверждения
    send_verification_email(email, verification_token, tenant_name)
    
    return user


def verify_email(db: Session, token: str) -> Optional[models.User]:
    """Подтверждает email пользователя"""
    user = db.query(models.User).filter(models.User.verification_token == token).first()
    if not user:
        return None
    
    user.is_verified = True
    user.verification_token = None
    db.commit()
    db.refresh(user)
    
    return user 
