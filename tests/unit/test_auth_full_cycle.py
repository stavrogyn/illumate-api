#!/usr/bin/env python3
"""
Тест полного цикла аутентификации с подтверждением email
"""

import os
import sys
import json
from unittest.mock import patch

# Добавляем текущую директорию в путь
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fastapi.testclient import TestClient
from app.main import app
from app.infrastructure.database.database_factory import DatabaseFactory
from app.infrastructure.database.mock_database import MockDatabase


def test_full_auth_cycle():
    """Тест полного цикла: регистрация -> подтверждение email -> вход -> получение данных пользователя"""
    print("🚀 Тестирование полного цикла аутентификации")
    
    # Патчим DatabaseFactory для использования мок-базы
    with patch('app.main.DatabaseFactory.create_database', return_value=MockDatabase()):
        with patch('app.infrastructure.external.email_service.email_service.send_verification_email', return_value=True):
            with patch('app.infrastructure.external.email_service.email_service.send_welcome_email', return_value=True):
                client = TestClient(app)
        
                # 1. Регистрация пользователя
                print("\n1. Регистрация пользователя...")
                register_data = {
                    "email": "fullcycle@example.com",
                    "password": "testpassword123",
                    "tenant_name": "Full Cycle Test Practice",
                    "role": "therapist",
                    "locale": "ru"
                }
                
                response = client.post("/auth/register", json=register_data)
                print(f"Status: {response.status_code}")
                
                if response.status_code == 201:
                    print("✅ Регистрация успешна")
                    user_data = response.json()
                    user_id = user_data["user_id"]
                    print(f"User ID: {user_id}")
                else:
                    print(f"❌ Ошибка регистрации: {response.text}")
                    assert False, f"Ошибка регистрации: {response.text}"
                
                # 2. Получаем verification token из мок-базы
                print("\n2. Получение verification token...")
                mock_db = DatabaseFactory.create_database()
                user = mock_db.get_user_by_email("fullcycle@example.com")
                
                assert user and user.get("verification_token"), "Verification token не найден"
                verification_token = user["verification_token"]
                print(f"✅ Verification token получен: {verification_token[:20]}...")
                
                # 3. Подтверждаем email
                print("\n3. Подтверждение email...")
                response = client.get(f"/auth/verify?token={verification_token}")
                print(f"Status: {response.status_code}")
                
                assert response.status_code == 200, f"Ошибка подтверждения email: {response.text}"
                print("✅ Email подтвержден")
                print(f"Response: {response.json()}")
                
                # 4. Попытка входа после подтверждения
                print("\n4. Вход после подтверждения email...")
                login_data = {
                    "email": "fullcycle@example.com",
                    "password": "testpassword123"
                }
                
                response = client.post("/auth/login", json=login_data)
                print(f"Status: {response.status_code}")
                
                assert response.status_code == 200, f"Ошибка входа: {response.text}"
                print("✅ Вход успешен")
                login_response = response.json()
                print(f"Response: {json.dumps(login_response, indent=2)}")
                
                # Проверяем, что в ответе есть session cookie
                cookies = response.cookies
                print(f"Все cookies: {dict(cookies)}")
                assert "session_token" in cookies, f"Session cookie не найден. Доступные cookies: {list(cookies.keys())}"
                print(f"✅ Session cookie установлен: {cookies['session_token'][:20]}...")
                
                # 5. Получение информации о пользователе с токеном
                print("\n5. Получение информации о пользователе...")
                response = client.get("/auth/me")
                print(f"Status: {response.status_code}")
                
                assert response.status_code == 200, f"Ошибка получения информации о пользователе: {response.text}"
                print("✅ Информация о пользователе получена")
                user_info = response.json()
                print(f"User info: {json.dumps(user_info, indent=2)}")
                
                # Проверяем, что данные корректны
                assert user_info["email"] == "fullcycle@example.com"
                assert user_info["role"] == "therapist"
                assert user_info["is_verified"] == True
                print("✅ Данные пользователя корректны")
                
                # 6. Проверка состояния мок-базы после всех операций
                print("\n6. Проверка состояния мок-базы...")
                tenants = mock_db.get_tenants()
                
                # Получаем tenant_id для получения пользователей
                assert len(tenants) > 0, "Нет tenants в базе данных"
                tenant_id = tenants[0]['id']
                users = mock_db.get_users(tenant_id)
                
                print(f"Количество tenants: {len(tenants)}")
                print(f"Количество users: {len(users)}")
                
                # Проверяем, что пользователь подтвержден в базе
                updated_user = mock_db.get_user_by_email("fullcycle@example.com")
                assert updated_user and updated_user.get("is_verified"), "Пользователь не подтвержден в базе данных"
                print("✅ Пользователь подтвержден в базе данных")
                
                print("\n✅ Полный цикл аутентификации прошел успешно!")


def test_verification_with_invalid_token():
    """Тест подтверждения email с неверным токеном"""
    print("\n🧪 Тестирование подтверждения с неверным токеном")
    
    with patch('app.main.DatabaseFactory.create_database', return_value=MockDatabase()):
        with patch('app.infrastructure.external.email_service.email_service.send_verification_email', return_value=True):
            with patch('app.infrastructure.external.email_service.email_service.send_welcome_email', return_value=True):
                client = TestClient(app)
        
                # Попытка подтверждения с неверным токеном
                response = client.get("/auth/verify?token=invalid-token-123")
                print(f"Status: {response.status_code}")
                
                if response.status_code == 400:
                    print("✅ Правильно отклонен неверный токен")
                    print(f"Response: {response.json()}")
                else:
                    print(f"❌ Неожиданный статус: {response.status_code}")


def test_login_with_wrong_password():
    """Тест входа с неверным паролем"""
    print("\n🧪 Тестирование входа с неверным паролем")
    
    with patch('app.main.DatabaseFactory.create_database', return_value=MockDatabase()):
        with patch('app.infrastructure.external.email_service.email_service.send_verification_email', return_value=True):
            with patch('app.infrastructure.external.email_service.email_service.send_welcome_email', return_value=True):
                client = TestClient(app)
        
                # Сначала регистрируем пользователя
                register_data = {
                    "email": "wrongpass@example.com",
                    "password": "correctpassword",
                    "tenant_name": "Wrong Pass Test",
                    "role": "therapist"
                }
                
                response = client.post("/auth/register", json=register_data)
                if response.status_code != 201:
                    print("❌ Ошибка регистрации для теста")
                    return
                
                # Подтверждаем email
                mock_db = DatabaseFactory.create_database()
                user = mock_db.get_user_by_email("wrongpass@example.com")
                if user and user.get("verification_token"):
                    client.get(f"/auth/verify?token={user['verification_token']}")
                
                # Попытка входа с неверным паролем
                login_data = {
                    "email": "wrongpass@example.com",
                    "password": "wrongpassword"
                }
                
                response = client.post("/auth/login", json=login_data)
                print(f"Status: {response.status_code}")
                
                if response.status_code == 401:
                    print("✅ Правильно отклонен неверный пароль")
                    print(f"Response: {response.json()}")
                else:
                    print(f"❌ Неожиданный статус: {response.status_code}")


def test_logout():
    """Тест выхода из системы"""
    print("\n🧪 Тестирование выхода из системы")
    
    with patch('app.main.DatabaseFactory.create_database', return_value=MockDatabase()):
        with patch('app.infrastructure.external.email_service.email_service.send_verification_email', return_value=True):
            with patch('app.infrastructure.external.email_service.email_service.send_welcome_email', return_value=True):
                client = TestClient(app)
        
                # Сначала регистрируем и входим
                register_data = {
                    "email": "logout@example.com",
                    "password": "testpassword",
                    "tenant_name": "Logout Test",
                    "role": "therapist"
                }
                
                response = client.post("/auth/register", json=register_data)
                if response.status_code != 201:
                    print("❌ Ошибка регистрации для теста")
                    return
                
                # Подтверждаем email
                mock_db = DatabaseFactory.create_database()
                user = mock_db.get_user_by_email("logout@example.com")
                if user and user.get("verification_token"):
                    client.get(f"/auth/verify?token={user['verification_token']}")
                
                # Входим
                login_data = {
                    "email": "logout@example.com",
                    "password": "testpassword"
                }
                
                response = client.post("/auth/login", json=login_data)
                if response.status_code != 200:
                    print("❌ Ошибка входа для теста")
                    return
                
                # Проверяем, что можем получить информацию о пользователе
                response = client.get("/auth/me")
                if response.status_code != 200:
                    print("❌ Не можем получить информацию о пользователе")
                    return
                
                # Выходим
                response = client.post("/auth/logout")
                print(f"Status: {response.status_code}")
                
                if response.status_code == 200:
                    print("✅ Выход успешен")
                    print(f"Response: {response.json()}")
                    
                    # Проверяем, что после выхода не можем получить информацию о пользователе
                    response = client.get("/auth/me")
                    if response.status_code == 401:
                        print("✅ После выхода доступ к /auth/me правильно отклонен")
                    else:
                        print(f"❌ После выхода неожиданный статус /auth/me: {response.status_code}")
                else:
                    print(f"❌ Ошибка выхода: {response.text}")


if __name__ == "__main__":
    print("=== Тестирование полного цикла аутентификации ===")
    
    test_full_auth_cycle()
    test_verification_with_invalid_token()
    test_login_with_wrong_password()
    test_logout()
    
    print("\n=== Все тесты завершены ===") 
