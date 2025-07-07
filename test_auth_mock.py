import os
import requests
import json
from unittest.mock import patch
from fastapi.testclient import TestClient
from main import app
from database_factory import DatabaseFactory
from mock_database import MockDatabase

# Устанавливаем переменную окружения для использования мок-базы
os.environ["DATABASE_TYPE"] = "mock"
os.environ["TESTING"] = "true"

# Создаем тестовый клиент
client = TestClient(app)

# Создаем мок-базу для тестов
mock_db = MockDatabase()


def get_mock_database():
    """Dependency для получения мок-базы данных"""
    return mock_db


def test_auth_flow():
    """Тестирует полный flow аутентификации с мок-базой данных"""
    
    print("=== Тестирование аутентификации с мок-базой данных ===\n")
    
    # Очищаем мок-базу перед тестами
    mock_db.clear()
    
    # Патчим DatabaseFactory.create_database чтобы возвращать мок-базу
    with patch('main.DatabaseFactory.create_database', return_value=mock_db):
        with patch('email_service.email_service.send_verification_email', return_value=True):
            with patch('email_service.email_service.send_welcome_email', return_value=True):
                
                # 1. Регистрация нового пользователя
                print("1. Регистрация пользователя...")
                register_data = {
                    "email": "test@example.com",
                    "password": "testpassword123",
                    "tenant_name": "Test Therapy Practice",
                    "role": "therapist",
                    "locale": "ru"
                }
                
                response = client.post("/auth/register", json=register_data)
                print(f"Status: {response.status_code}")
                if response.status_code == 201:
                    print("✅ Регистрация успешна")
                    print(f"Response: {response.json()}")
                    # Проверим состояние мок-базы сразу после регистрации
                    print(f"  После регистрации - tenants: {len(mock_db.tenants)}, users: {len(mock_db.users)}")
                else:
                    print(f"❌ Ошибка регистрации: {response.text}")
                    return
                
                print("\n" + "="*50 + "\n")
                
                # 2. Попытка входа без подтверждения email
                print("2. Попытка входа без подтверждения email...")
                login_data = {
                    "email": "test@example.com",
                    "password": "testpassword123"
                }
                
                response = client.post("/auth/login", json=login_data)
                print(f"Status: {response.status_code}")
                if response.status_code == 401:
                    print("✅ Правильно отклонен вход без подтверждения email")
                    print(f"Response: {response.json()}")
                else:
                    print(f"❌ Неожиданный ответ: {response.text}")
                
                print("\n" + "="*50 + "\n")
                
                # 3. Получение информации о пользователе (должно требовать аутентификации)
                print("3. Попытка получить информацию о пользователе без токена...")
                response = client.get("/auth/me")
                print(f"Status: {response.status_code}")
                if response.status_code == 401:
                    print("✅ Правильно отклонен доступ без токена")
                else:
                    print(f"❌ Неожиданный ответ: {response.text}")
                
                print("\n" + "="*50 + "\n")
                
                # 4. Проверка health endpoint
                print("4. Проверка health endpoint...")
                response = client.get("/health")
                print(f"Status: {response.status_code}")
                if response.status_code == 200:
                    print("✅ Health endpoint работает")
                    print(f"Response: {response.json()}")
                else:
                    print(f"❌ Ошибка health endpoint: {response.text}")
                
                print("\n" + "="*50 + "\n")
                
                # 5. Проверка документации API
                print("5. Проверка документации API...")
                response = client.get("/docs")
                print(f"Status: {response.status_code}")
                if response.status_code == 200:
                    print("✅ Документация API доступна")
                else:
                    print(f"❌ Ошибка документации API: {response.text}")
                
                print("\n" + "="*50 + "\n")
                
                # 6. Проверка повторной регистрации с тем же email
                print("6. Попытка повторной регистрации с тем же email...")
                response = client.post("/auth/register", json=register_data)
                print(f"Status: {response.status_code}")
                if response.status_code == 400:
                    print("✅ Правильно отклонена повторная регистрация")
                    print(f"Response: {response.json()}")
                else:
                    print(f"❌ Неожиданный ответ: {response.text}")
                    print(f"  При повторной регистрации - tenants: {len(mock_db.tenants)}, users: {len(mock_db.users)}")
                    print(f"  Email mapping: {mock_db.email_to_user}")
                
                print("\n" + "="*50 + "\n")
                
                # 7. Проверка состояния мок-базы
                print("7. Проверка состояния мок-базы...")
                print(f"Количество tenants: {len(mock_db.tenants)}")
                print(f"Количество users: {len(mock_db.users)}")
                print(f"Количество clients: {len(mock_db.clients)}")
                
                # Добавим детальную отладочную информацию
                print(f"Tenants: {list(mock_db.tenants.keys())}")
                print(f"Users: {list(mock_db.users.keys())}")
                print(f"Email to user mapping: {mock_db.email_to_user}")
                
                assert len(mock_db.tenants) == 1, f"Ожидался 1 tenant, найдено: {len(mock_db.tenants)}"
                assert len(mock_db.users) == 1, f"Ожидался 1 user, найдено: {len(mock_db.users)}"
                print("✅ Данные корректно сохранены в мок-базе")
    
    # Очищаем мок-базу после тестов
    mock_db.clear()


def test_multiple_runs():
    """Тестирует, что можно запускать тесты многократно без конфликтов"""
    
    print("\n=== Тестирование множественных запусков ===\n")
    
    for i in range(3):
        print(f"Запуск {i + 1}:")
        
        # Очищаем мок-базу перед каждым запуском
        mock_db.clear()
        
        with patch('main.DatabaseFactory.create_database', return_value=mock_db):
            with patch('email_service.email_service.send_verification_email', return_value=True):
                with patch('email_service.email_service.send_welcome_email', return_value=True):
                    
                    register_data = {
                        "email": f"test{i}@example.com",
                        "password": "testpassword123",
                        "tenant_name": f"Test Practice {i}",
                        "role": "therapist",
                        "locale": "ru"
                    }
                    
                    response = client.post("/auth/register", json=register_data)
                    assert response.status_code == 201, f"Ошибка регистрации {i + 1}: {response.text}"
                    print(f"  ✅ Регистрация {i + 1} успешна")
        
        print()


if __name__ == "__main__":
    test_auth_flow()
    test_multiple_runs()
    print("=== Все тесты завершены ===") 
