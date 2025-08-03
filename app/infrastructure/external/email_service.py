import os
import boto3
from botocore.exceptions import ClientError
from typing import Optional
from fastapi import BackgroundTasks
from app.config import settings

class EmailService:
    """Сервис для отправки писем через AWS SES"""
    
    def __init__(self):
        self.aws_region = settings.aws_region
        self.aws_access_key_id = settings.aws_access_key_id
        self.aws_secret_access_key = settings.aws_secret_access_key
        self.sender_email = settings.sender_email
        
        # Инициализация SES клиента только если есть AWS credentials
        self.ses_client = None
        if self.aws_access_key_id and self.aws_secret_access_key:
            try:
                self.ses_client = boto3.client(
                    "ses",
                    region_name=self.aws_region,
                    aws_access_key_id=self.aws_access_key_id,
                    aws_secret_access_key=self.aws_secret_access_key
                )
                print("✅ AWS SES client initialized successfully")
            except Exception as e:
                print(f"❌ Failed to initialize AWS SES client: {e}")
        else:
            print("⚠️ AWS credentials not provided, email service will use mock mode")
    
    def send_email(self, to_email: str, subject: str, body_text: str, body_html: str = "") -> bool:
        """
        Отправляет email через AWS SES
        
        Args:
            to_email: Email получателя
            subject: Тема письма
            body_text: Текстовое содержимое
            body_html: HTML содержимое (опционально)
            
        Returns:
            bool: True если письмо отправлено успешно, False в противном случае
        """
        if not self.ses_client:
            # Mock режим - просто выводим в консоль
            print(f"📧 MOCK EMAIL SENT:")
            print(f"   To: {to_email}")
            print(f"   Subject: {subject}")
            print(f"   Body: {body_text}")
            return True
        
        try:
            response = self.ses_client.send_email(
                Source=self.sender_email,
                Destination={"ToAddresses": [to_email]},
                Message={
                    "Subject": {"Data": subject},
                    "Body": {
                        "Text": {"Data": body_text},
                        "Html": {"Data": body_html or body_text},
                    },
                }
            )
            print(f"✅ Email sent successfully: {response['MessageId']}")
            return True
        except ClientError as e:
            print(f"❌ Failed to send email: {e.response['Error']['Message']}")
            return False
        except Exception as e:
            print(f"❌ Unexpected error sending email: {e}")
            return False
    
    def send_verification_email(self, to_email: str, verification_token: str, tenant_name: str, base_url: str = "http://localhost:8000") -> bool:
        """
        Отправляет письмо для подтверждения email
        
        Args:
            to_email: Email пользователя
            verification_token: Токен для подтверждения
            tenant_name: Название организации
            base_url: Базовый URL приложения
            
        Returns:
            bool: True если письмо отправлено успешно
        """
        subject = f"Подтверждение регистрации в {tenant_name}"
        
        verification_url = f"{base_url}/auth/verify?token={verification_token}"
        
        body_text = f"""
Здравствуйте!

Спасибо за регистрацию в {tenant_name}. Для подтверждения вашего email перейдите по ссылке:

{verification_url}

Если вы не регистрировались в нашем сервисе, проигнорируйте это письмо.

С уважением,
Команда {tenant_name}
        """.strip()
        
        body_html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Подтверждение регистрации</title>
</head>
<body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
    <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
        <h2 style="color: #2c3e50;">Подтверждение регистрации</h2>
        
        <p>Здравствуйте!</p>
        
        <p>Спасибо за регистрацию в <strong>{tenant_name}</strong>. Для подтверждения вашего email нажмите на кнопку ниже:</p>
        
        <div style="text-align: center; margin: 30px 0;">
            <a href="{verification_url}" 
               style="background-color: #3498db; color: white; padding: 12px 24px; text-decoration: none; border-radius: 5px; display: inline-block;">
                Подтвердить Email
            </a>
        </div>
        
        <p>Или скопируйте эту ссылку в браузер:</p>
        <p style="word-break: break-all; color: #7f8c8d;">{verification_url}</p>
        
        <hr style="border: none; border-top: 1px solid #ecf0f1; margin: 30px 0;">
        
        <p style="font-size: 14px; color: #7f8c8d;">
            Если вы не регистрировались в нашем сервисе, проигнорируйте это письмо.
        </p>
        
        <p style="font-size: 14px; color: #7f8c8d;">
            С уважением,<br>
            Команда {tenant_name}
        </p>
    </div>
</body>
</html>
        """
        
        return self.send_email(to_email, subject, body_text, body_html)
    
    def send_welcome_email(self, to_email: str, tenant_name: str) -> bool:
        """
        Отправляет приветственное письмо после подтверждения email
        
        Args:
            to_email: Email пользователя
            tenant_name: Название организации
            
        Returns:
            bool: True если письмо отправлено успешно
        """
        subject = f"Добро пожаловать в {tenant_name}!"
        
        body_text = f"""
Здравствуйте!

Добро пожаловать в {tenant_name}! Ваш email успешно подтвержден.

Теперь вы можете войти в систему и начать работу.

С уважением,
Команда {tenant_name}
        """.strip()
        
        body_html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Добро пожаловать</title>
</head>
<body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
    <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
        <h2 style="color: #27ae60;">Добро пожаловать!</h2>
        
        <p>Здравствуйте!</p>
        
        <p>Добро пожаловать в <strong>{tenant_name}</strong>! Ваш email успешно подтвержден.</p>
        
        <p>Теперь вы можете войти в систему и начать работу.</p>
        
        <hr style="border: none; border-top: 1px solid #ecf0f1; margin: 30px 0;">
        
        <p style="font-size: 14px; color: #7f8c8d;">
            С уважением,<br>
            Команда {tenant_name}
        </p>
    </div>
</body>
</html>
        """
        
        return self.send_email(to_email, subject, body_text, body_html)


# Создаем глобальный экземпляр сервиса
email_service = EmailService() 
