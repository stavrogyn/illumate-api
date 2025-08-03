import os
from typing import Optional
from app.domain.repositories.database_interface import DatabaseInterface
from app.infrastructure.database.mock_database import MockDatabase
from app.infrastructure.database.real_database import RealDatabase
from sqlalchemy.orm import Session


class DatabaseFactory:
    """Фабрика для создания экземпляров базы данных"""
    
    @staticmethod
    def create_database(db_session: Optional[Session] = None) -> DatabaseInterface:
        """
        Создает экземпляр базы данных в зависимости от окружения
        
        Args:
            db_session: SQLAlchemy сессия (только для реальной БД)
            
        Returns:
            Экземпляр DatabaseInterface
        """
        # Проверяем переменную окружения для выбора типа БД
        database_type = os.getenv("DATABASE_TYPE", "real").lower()
        
        if database_type == "mock":
            return MockDatabase()
        elif database_type == "real":
            if db_session is None:
                raise ValueError("db_session is required for real database")
            return RealDatabase(db_session)
        else:
            raise ValueError(f"Unknown database type: {database_type}")
    
    @staticmethod
    def is_test_environment() -> bool:
        """Проверяет, находимся ли мы в тестовом окружении"""
        return os.getenv("TESTING", "false").lower() == "true" or \
               os.getenv("DATABASE_TYPE", "real").lower() == "mock" 
