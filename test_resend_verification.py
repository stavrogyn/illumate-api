#!/usr/bin/env python3
"""
Тест для endpoint повторной отправки верификации email
"""

import os
import sys
import json
from unittest.mock import patch

# Добавляем текущую директорию в путь
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fastapi.testclient import TestClient
from main import app
from database_factory import DatabaseFactory, MockDatabase


def test_resend_verification_success():
    """Тест успешной повторной отправки верификации"""
    print("🧪 Тестирование успешной повторной отправки верификации")
    
    # Очищаем AWS credentials для использования mock режима
    with patch.dict(os.environ, {}, clear=True):
        with patch.object(DatabaseFactory, 'create_database', return_value=MockDatabase()):
            with patch('email_service.email_service.send_verification_email', return_value=True):
                client = TestClient(app)
                
                # 1. Регистрируем пользователя
                register_data = {
                    "email": "resend@example.com",
                    "password": "testpassword123",
                    "tenant_name": "Resend Test Practice",
                    "role": "therapist"
                }
                
                response = client.post("/auth/register", json=register_data)
                assert response.status_code == 201, f"Ошибка регистрации: {response.text}"
                print("✅ Пользователь зарегистрирован")
                
                # 2. Получаем первый verification token
                mock_db = DatabaseFactory.create_database()
                user = mock_db.get_user_by_email("resend@example.com")
                assert user and user.get("verification_token"), "Verification token не найден"
                first_token = user["verification_token"]
                print(f"✅ Первый token: {first_token[:20]}...")
                
                # 3. Запрашиваем повторную отправку верификации
                resend_data = {"email": "resend@example.com"}
                response = client.post("/auth/resend-verification", json=resend_data)
                
                assert response.status_code == 200, f"Ошибка повторной отправки: {response.text}"
                print("✅ Повторная отправка успешна")
                
                response_data = response.json()
                assert response_data["message"] == "Verification email sent successfully"
                assert response_data["email"] == "resend@example.com"
                
                # 4. Проверяем, что токен изменился
                updated_user = mock_db.get_user_by_email("resend@example.com")
                assert updated_user and updated_user.get("verification_token"), "Новый verification token не найден"
                second_token = updated_user["verification_token"]
                print(f"✅ Новый token: {second_token[:20]}...")
                
                assert first_token != second_token, "Токен не изменился"
                assert not updated_user["is_verified"], "Пользователь не должен быть подтвержден"
                
                print("✅ Токен успешно обновлен")


def test_resend_verification_user_not_found():
    """Тест повторной отправки для несуществующего пользователя"""
    print("\n🧪 Тестирование повторной отправки для несуществующего пользователя")
    
    with patch.dict(os.environ, {}, clear=True):
        with patch.object(DatabaseFactory, 'create_database', return_value=MockDatabase()):
            with patch('email_service.email_service.send_verification_email', return_value=True):
                client = TestClient(app)
                
                resend_data = {"email": "nonexistent@example.com"}
                response = client.post("/auth/resend-verification", json=resend_data)
                
                assert response.status_code == 404, f"Неожиданный статус: {response.status_code}"
                print("✅ Правильно отклонен несуществующий пользователь")
                
                response_data = response.json()
                assert response_data["detail"] == "User not found"


def test_resend_verification_already_verified():
    """Тест повторной отправки для уже подтвержденного email"""
    print("\n🧪 Тестирование повторной отправки для уже подтвержденного email")
    
    with patch.dict(os.environ, {}, clear=True):
        with patch.object(DatabaseFactory, 'create_database', return_value=MockDatabase()):
            with patch('email_service.email_service.send_verification_email', return_value=True):
                with patch('email_service.email_service.send_welcome_email', return_value=True):
                    client = TestClient(app)
                    
                    # 1. Регистрируем пользователя
                    register_data = {
                        "email": "verified@example.com",
                        "password": "testpassword123",
                        "tenant_name": "Verified Test Practice",
                        "role": "therapist"
                    }
                    
                    response = client.post("/auth/register", json=register_data)
                    assert response.status_code == 201, f"Ошибка регистрации: {response.text}"
                    
                    # 2. Подтверждаем email
                    mock_db = DatabaseFactory.create_database()
                    user = mock_db.get_user_by_email("verified@example.com")
                    assert user and user.get("verification_token"), "Verification token не найден"
                    
                    response = client.get(f"/auth/verify?token={user['verification_token']}")
                    assert response.status_code == 200, f"Ошибка подтверждения: {response.text}"
                    
                    # 3. Пытаемся отправить повторную верификацию
                    resend_data = {"email": "verified@example.com"}
                    response = client.post("/auth/resend-verification", json=resend_data)
                    
                    assert response.status_code == 400, f"Неожиданный статус: {response.status_code}"
                    print("✅ Правильно отклонен уже подтвержденный email")
                    
                    response_data = response.json()
                    assert response_data["detail"] == "Email is already verified"


def test_resend_verification_invalid_email():
    """Тест повторной отправки с неверным форматом email"""
    print("\n🧪 Тестирование повторной отправки с неверным форматом email")
    
    with patch.dict(os.environ, {}, clear=True):
        with patch.object(DatabaseFactory, 'create_database', return_value=MockDatabase()):
            with patch('email_service.email_service.send_verification_email', return_value=True):
                client = TestClient(app)
                
                resend_data = {"email": "invalid-email"}
                response = client.post("/auth/resend-verification", json=resend_data)
                
                assert response.status_code == 422, f"Неожиданный статус: {response.status_code}"
                print("✅ Правильно отклонен неверный формат email")


def test_resend_verification_multiple_requests():
    """Тест множественных запросов на повторную отправку"""
    print("\n🧪 Тестирование множественных запросов на повторную отправку")
    
    with patch.dict(os.environ, {}, clear=True):
        with patch.object(DatabaseFactory, 'create_database', return_value=MockDatabase()):
            with patch('email_service.email_service.send_verification_email', return_value=True):
                client = TestClient(app)
                
                # 1. Регистрируем пользователя
                register_data = {
                    "email": "multiple@example.com",
                    "password": "testpassword123",
                    "tenant_name": "Multiple Test Practice",
                    "role": "therapist"
                }
                
                response = client.post("/auth/register", json=register_data)
                assert response.status_code == 201, f"Ошибка регистрации: {response.text}"
                
                # 2. Получаем первый токен
                mock_db = DatabaseFactory.create_database()
                user = mock_db.get_user_by_email("multiple@example.com")
                first_token = user["verification_token"]
                
                # 3. Отправляем несколько запросов на повторную отправку
                resend_data = {"email": "multiple@example.com"}
                
                for i in range(3):
                    response = client.post("/auth/resend-verification", json=resend_data)
                    assert response.status_code == 200, f"Ошибка запроса {i+1}: {response.text}"
                    print(f"✅ Запрос {i+1} успешен")
                
                # 4. Проверяем, что токен изменился после каждого запроса
                updated_user = mock_db.get_user_by_email("multiple@example.com")
                final_token = updated_user["verification_token"]
                
                assert first_token != final_token, "Токен не изменился после множественных запросов"
                print("✅ Токен корректно обновлялся при множественных запросах")


if __name__ == "__main__":
    print("=== Тестирование endpoint повторной отправки верификации ===")
    
    test_resend_verification_success()
    test_resend_verification_user_not_found()
    test_resend_verification_already_verified()
    test_resend_verification_invalid_email()
    test_resend_verification_multiple_requests()
    
    print("\n=== Все тесты завершены ===") 
