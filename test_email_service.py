#!/usr/bin/env python3
"""
Тест для проверки email сервиса
"""

import os
import sys
from unittest.mock import patch, MagicMock

# Добавляем текущую директорию в путь
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from email_service import EmailService


def test_email_service_mock_mode():
    """Тест email сервиса в mock режиме (без AWS credentials)"""
    print("\n🧪 1. Testing Email Service in Mock Mode")
    
    # Очищаем AWS credentials из окружения
    with patch.dict(os.environ, {}, clear=True):
        email_service = EmailService()
        
        # Проверяем, что SES клиент не инициализирован
        assert email_service.ses_client is None
        
        # Тестируем отправку verification email
        result = email_service.send_verification_email(
            "test@example.com",
            "test-token-123",
            "Test Company",
            "http://localhost:8000"
        )
        
        assert result is True, "Mock email service did not return True"
        print("✅ Mock email service works correctly \n")


def test_email_service_with_aws_credentials():
    """Тест email сервиса с AWS credentials (mock SES)"""
    print("\n🧪 2. Testing Email Service with AWS Credentials")
    
    # Мокаем AWS credentials
    with patch.dict(os.environ, {
        "AWS_REGION": "us-east-1",
        "AWS_ACCESS_KEY_ID": "test-key",
        "AWS_SECRET_ACCESS_KEY": "test-secret",
        "SENDER_EMAIL": "test@example.com"
    }):
        # Мокаем boto3.client
        mock_ses_client = MagicMock()
        mock_response = {"MessageId": "test-message-id"}
        mock_ses_client.send_email.return_value = mock_response
        
        with patch('boto3.client', return_value=mock_ses_client):
            email_service = EmailService()
            
            # Проверяем, что SES клиент инициализирован
            assert email_service.ses_client is not None
            
            # Тестируем отправку verification email
            result = email_service.send_verification_email(
                "test@example.com",
                "test-token-123",
                "Test Company",
                "http://localhost:8000"
            )
            
            assert result is True, "SES email service did not return True"
            assert mock_ses_client.send_email.called, "SES send_email was not called"
            
            # Проверяем параметры вызова
            call_args = mock_ses_client.send_email.call_args
            assert call_args[1]['Source'] == "test@example.com"
            assert call_args[1]['Destination']['ToAddresses'] == ["test@example.com"]
            assert "Подтверждение регистрации" in call_args[1]['Message']['Subject']['Data']
            
            print("✅ AWS SES email service works correctly \n")


def test_welcome_email():
    """Тест отправки приветственного письма"""
    print("\n🧪 3. Testing Welcome Email")
    
    with patch.dict(os.environ, {}, clear=True):
        email_service = EmailService()
        
        result = email_service.send_welcome_email(
            "test@example.com",
            "Test Company"
        )
        
        assert result is True, "Welcome email service did not return True"
        print("✅ Welcome email service works correctly \n")


def test_email_service_error_handling():
    """Тест обработки ошибок в email сервисе"""
    print("\n🧪 4. Testing Email Service Error Handling")
    
    # Мокаем AWS credentials
    with patch.dict(os.environ, {
        "AWS_REGION": "us-east-1",
        "AWS_ACCESS_KEY_ID": "test-key",
        "AWS_SECRET_ACCESS_KEY": "test-secret",
        "SENDER_EMAIL": "test@example.com"
    }):
        # Мокаем boto3.client с ошибкой
        mock_ses_client = MagicMock()
        mock_ses_client.send_email.side_effect = Exception("AWS SES Error")
        
        with patch('boto3.client', return_value=mock_ses_client):
            email_service = EmailService()
            
            # Тестируем обработку ошибки
            result = email_service.send_email(
                "test@example.com",
                "Test Subject",
                "Test Body"
            )
            
            assert result is False, "Error handling did not return False"
            print("✅ Error handling works correctly \n")


if __name__ == "__main__":
    print("🚀 Starting Email Service Tests")
    
    test_email_service_mock_mode()
    test_email_service_with_aws_credentials()
    test_welcome_email()
    test_email_service_error_handling()
    
    print("\n✅ All email service tests passed!") 
