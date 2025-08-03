#!/usr/bin/env python3
"""
Database setup script for FastAPI application.
This script helps initialize the database and create tables.
"""

import os
import sys

# Добавляем корневую директорию проекта в sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine, text
from app.infrastructure.database.database import get_engine
from app.infrastructure.database.models import Base
from app.config import settings

def create_database():
    """Create the database if it doesn't exist."""
    # Connect to PostgreSQL server (not to a specific database)
    db_url = settings.database_url
    db_name = db_url.split('/')[-1]
    server_url = '/'.join(db_url.split('/')[:-1]) + '/postgres'
    
    try:
        # Connect to default postgres database
        engine_server = create_engine(server_url)
        with engine_server.connect() as conn:
            # Check if database exists
            result = conn.execute(text(f"SELECT 1 FROM pg_database WHERE datname = '{db_name}'"))
            if not result.fetchone():
                # Create database
                conn.execute(text(f"CREATE DATABASE {db_name}"))
                print(f"Database '{db_name}' created successfully!")
            else:
                print(f"Database '{db_name}' already exists.")
        engine_server.dispose()
    except Exception as e:
        print(f"Error creating database: {e}")
        print("Please make sure PostgreSQL is running and you have the correct permissions.")
        return False
    
    return True

def create_tables():
    """Create all tables defined in models."""
    try:
        engine = get_engine()
        Base.metadata.create_all(bind=engine)
        print("Tables created successfully!")
        return True
    except Exception as e:
        print(f"Error creating tables: {e}")
        return False

def main():
    """Main function to set up the database."""
    print("Setting up database for FastAPI application...")
    print(f"Database URL: {settings.database_url}")
    
    # Create database
    if not create_database():
        sys.exit(1)
    
    # Create tables
    if not create_tables():
        sys.exit(1)
    
    print("Database setup completed successfully!")
    print("\nNext steps:")
    print("1. Run 'alembic upgrade head' to apply migrations")
    print("2. Start the application with 'uvicorn main:app --reload'")

if __name__ == "__main__":
    main() 
