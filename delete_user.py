#!/usr/bin/env python3
"""
Скрипт для удаления пользователя из базы данных
"""

import os
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from database_factory import DatabaseFactory
from mock_database import MockDatabase
from config import settings

def get_db_session():
    """Создает сессию базы данных"""
    engine = create_engine(settings.database_url)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return SessionLocal()

def delete_user_by_email(email: str, use_mock: bool = False):
    """
    Удаляет пользователя по email
    
    Args:
        email: Email пользователя для удаления
        use_mock: Использовать мок-базу (для тестирования)
    """
    
    print(f"=== Удаление пользователя {email} ===")
    
    # Определяем тип базы данных
    if use_mock:
        print("🔧 Используется мок-база данных")
        db = MockDatabase()
        
        # Ищем пользователя
        print(f"\n🔍 Поиск пользователя с email: {email}")
        user = db.get_user_by_email(email)
        
        if not user:
            print("❌ Пользователь не найден")
            return False
        
        print("✅ Пользователь найден:")
        print(f"   ID: {user['id']}")
        print(f"   Email: {user['email']}")
        print(f"   Role: {user['role']}")
        print(f"   Verified: {user['is_verified']}")
        print(f"   Created: {user['created_at']}")
        
        # Подтверждение удаления
        confirm = input(f"\n⚠️ Вы уверены, что хотите удалить пользователя {email}? (y/N): ").strip().lower()
        
        if confirm not in ['y', 'yes', 'да']:
            print("❌ Удаление отменено")
            return False
        
        # Удаляем пользователя
        print(f"\n🗑️ Удаление пользователя...")
        
        try:
            # Удаляем из email mapping
            if hasattr(db, 'email_to_user') and email in db.email_to_user:
                del db.email_to_user[email]
                print("   ✅ Удален из email mapping")
            
            # Удаляем пользователя
            if user['id'] in db.users:
                del db.users[user['id']]
                print("   ✅ Удален из users")
            
            # Удаляем tenant если он больше не используется
            tenant_id = user.get('tenant_id')
            if tenant_id and hasattr(db, 'tenants'):
                # Проверяем, есть ли еще пользователи в этом tenant
                other_users = [u for u in db.users.values() if u.get('tenant_id') == tenant_id]
                if not other_users and tenant_id in db.tenants:
                    del db.tenants[tenant_id]
                    print(f"   ✅ Удален tenant {tenant_id} (больше не используется)")
            
            print("✅ Пользователь успешно удален!")
            return True
            
        except Exception as e:
            print(f"❌ Ошибка при удалении: {e}")
            return False
    
    else:
        print("🗄️ Используется реальная база данных")
        
        # Создаем сессию базы данных
        db_session = get_db_session()
        
        try:
            # Ищем пользователя
            print(f"\n🔍 Поиск пользователя с email: {email}")
            
            # SQL запрос для поиска пользователя
            query = text("""
                SELECT u.id, u.email, u.role, u.is_verified, u.created_at, u.tenant_id,
                       t.name as tenant_name
                FROM users u
                LEFT JOIN tenants t ON u.tenant_id = t.id
                WHERE u.email = :email
            """)
            
            result = db_session.execute(query, {"email": email})
            user_data = result.fetchone()
            
            if not user_data:
                print("❌ Пользователь не найден")
                return False
            
            print("✅ Пользователь найден:")
            print(f"   ID: {user_data.id}")
            print(f"   Email: {user_data.email}")
            print(f"   Role: {user_data.role}")
            print(f"   Verified: {user_data.is_verified}")
            print(f"   Created: {user_data.created_at}")
            print(f"   Tenant: {user_data.tenant_name or 'N/A'}")
            
            # Подтверждение удаления
            confirm = input(f"\n⚠️ Вы уверены, что хотите удалить пользователя {email}? (y/N): ").strip().lower()
            
            if confirm not in ['y', 'yes', 'да']:
                print("❌ Удаление отменено")
                return False
            
            # Удаляем пользователя
            print(f"\n🗑️ Удаление пользователя...")
            
            # Удаляем пользователя
            delete_user_query = text("DELETE FROM users WHERE email = :email")
            result = db_session.execute(delete_user_query, {"email": email})
            
            if result.rowcount > 0:
                print("   ✅ Пользователь удален из базы данных")
                
                # Проверяем, нужно ли удалить tenant
                if user_data.tenant_id:
                    # Проверяем, есть ли еще пользователи в этом tenant
                    check_tenant_query = text("SELECT COUNT(*) FROM users WHERE tenant_id = :tenant_id")
                    result = db_session.execute(check_tenant_query, {"tenant_id": user_data.tenant_id})
                    user_count = result.scalar()
                    
                    if user_count == 0:
                        # Удаляем tenant
                        delete_tenant_query = text("DELETE FROM tenants WHERE id = :tenant_id")
                        db_session.execute(delete_tenant_query, {"tenant_id": user_data.tenant_id})
                        print(f"   ✅ Tenant {user_data.tenant_id} удален (больше не используется)")
                
                # Подтверждаем изменения
                db_session.commit()
                print("✅ Пользователь успешно удален!")
                return True
            else:
                print("❌ Пользователь не был удален")
                return False
                
        except Exception as e:
            print(f"❌ Ошибка при удалении: {e}")
            db_session.rollback()
            return False
        finally:
            db_session.close()

def list_all_users(use_mock: bool = False):
    """Показывает список всех пользователей"""
    
    print("=== Список всех пользователей ===")
    
    if use_mock:
        db = MockDatabase()
        
        if not db.users:
            print("📭 База данных пуста")
            return
        
        print(f"\nНайдено пользователей: {len(db.users)}")
        print("-" * 80)
        
        for user_id, user in db.users.items():
            print(f"ID: {user_id}")
            print(f"Email: {user['email']}")
            print(f"Role: {user['role']}")
            print(f"Verified: {user['is_verified']}")
            print(f"Created: {user['created_at']}")
            print("-" * 80)
    
    else:
        # Создаем сессию базы данных
        db_session = get_db_session()
        
        try:
            # SQL запрос для получения всех пользователей
            query = text("""
                SELECT u.id, u.email, u.role, u.is_verified, u.created_at,
                       t.name as tenant_name
                FROM users u
                LEFT JOIN tenants t ON u.tenant_id = t.id
                ORDER BY u.created_at DESC
            """)
            
            result = db_session.execute(query)
            users = result.fetchall()
            
            if not users:
                print("📭 База данных пуста")
                return
            
            print(f"\nНайдено пользователей: {len(users)}")
            print("-" * 80)
            
            for user in users:
                print(f"ID: {user.id}")
                print(f"Email: {user.email}")
                print(f"Role: {user.role}")
                print(f"Verified: {user.is_verified}")
                print(f"Created: {user.created_at}")
                print(f"Tenant: {user.tenant_name or 'N/A'}")
                print("-" * 80)
                
        except Exception as e:
            print(f"❌ Ошибка при получении списка пользователей: {e}")
        finally:
            db_session.close()

def main():
    """Главная функция"""
    
    if len(sys.argv) < 2:
        print("Использование:")
        print("  python delete_user.py <email> [--mock]")
        print("  python delete_user.py --list [--mock]")
        print("\nПримеры:")
        print("  python delete_user.py nikitakrugovoi@gmail.com")
        print("  python delete_user.py nikitakrugovoi@gmail.com --mock")
        print("  python delete_user.py --list")
        return
    
    use_mock = "--mock" in sys.argv
    
    if "--list" in sys.argv:
        list_all_users(use_mock)
    else:
        email = sys.argv[1]
        if email.startswith("--"):
            print("❌ Неверный email")
            return
        
        delete_user_by_email(email, use_mock)

if __name__ == "__main__":
    main() 
