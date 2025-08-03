#!/usr/bin/env python3
"""
Test script to verify that all imports work correctly
"""

import os
import sys

# Добавляем корневую директорию проекта в sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_imports():
    """Test all critical imports"""
    print("Testing imports...")
    
    try:
        # Test app imports
        from app.config import settings
        print("✅ app.config.settings imported successfully")
        
        from app.infrastructure.database.database import get_engine, get_db
        print("✅ app.infrastructure.database.database imported successfully")
        
        from app.infrastructure.database.models import Base
        print("✅ app.infrastructure.database.models imported successfully")
        
        from app.infrastructure.database.database_factory import DatabaseFactory
        print("✅ app.infrastructure.database.database_factory imported successfully")
        
        from app.infrastructure.external.email_service import EmailService
        print("✅ app.infrastructure.external.email_service imported successfully")
        
        from app.domain.services.auth_service import verify_password, get_password_hash
        print("✅ app.domain.services.auth_service imported successfully")
        
        from app.application.schemas import UserCreate, ClientCreate, TenantCreate
        print("✅ app.application.schemas imported successfully")
        
        print("\n🎉 All imports successful!")
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

if __name__ == "__main__":
    success = test_imports()
    sys.exit(0 if success else 1) 
