import requests
import json
import os
import subprocess
from sqlalchemy import create_engine, text
from fastapi.testclient import TestClient

os.environ["DATABASE_URL"] = "postgresql://postgres:password@localhost:5432/fastapi_test_db"

BASE_URL = "http://localhost:8000"

subprocess.run(["alembic", "upgrade", "head"])

def drop_all_data():
    engine = create_engine(os.environ["DATABASE_URL"])
    with engine.connect() as conn:
        conn.execute(text("DROP SCHEMA public CASCADE; CREATE SCHEMA public;"))

def test_auth_flow():
    """Тестирует полный flow аутентификации"""
    
    print("=== Тестирование аутентификации ===\n")
    
    # 1. Регистрация нового пользователя
    print("1. Регистрация пользователя...")
    register_data = {
        "email": "test@example.com",
        "password": "testpassword123",
        "tenant_name": "Test Therapy Practice",
        "role": "therapist",
        "locale": "ru"
    }
    
    response = requests.post(f"{BASE_URL}/auth/register", json=register_data)
    print(f"Status: {response.status_code}")
    if response.status_code == 201:
        print("✅ Регистрация успешна")
        print(f"Response: {response.json()}")
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
    
    response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
    print(f"Status: {response.status_code}")
    if response.status_code == 401:
        print("✅ Правильно отклонен вход без подтверждения email")
        print(f"Response: {response.json()}")
    else:
        print(f"❌ Неожиданный ответ: {response.text}")
    
    print("\n" + "="*50 + "\n")
    
    # 3. Получение информации о пользователе (должно требовать аутентификации)
    print("3. Попытка получить информацию о пользователе без токена...")
    response = requests.get(f"{BASE_URL}/auth/me")
    print(f"Status: {response.status_code}")
    if response.status_code == 401:
        print("✅ Правильно отклонен доступ без токена")
    else:
        print(f"❌ Неожиданный ответ: {response.text}")
    
    print("\n" + "="*50 + "\n")
    
    # 4. Проверка health endpoint
    print("4. Проверка health endpoint...")
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        print("✅ Health endpoint работает")
        print(f"Response: {response.json()}")
    else:
        print(f"❌ Ошибка health endpoint: {response.text}")
    
    print("\n" + "="*50 + "\n")
    
    # 5. Проверка документации API
    print("5. Проверка документации API...")
    response = requests.get(f"{BASE_URL}/docs")
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        print("✅ Документация API доступна")
    else:
        print(f"❌ Ошибка документации API: {response.text}")

if __name__ == "__main__":
    test_auth_flow() 
