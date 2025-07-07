#!/usr/bin/env python3
"""
Simple test script for the FastAPI application.
This script tests the basic API endpoints.
"""

import requests
import json
import time

BASE_URL = "http://localhost:8000"

def test_health():
    """Test the health endpoint."""
    print("Testing health endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            print("✅ Health check passed")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to the server. Make sure it's running.")
        return False

def test_create_user():
    """Test creating a user."""
    print("\nTesting user creation...")
    user_data = {
        "email": "test@example.com",
        "username": "testuser",
        "full_name": "Test User",
        "password": "testpassword123"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/users/",
            json=user_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 201:
            user = response.json()
            print(f"✅ User created successfully: {user['username']}")
            return user['id']
        else:
            print(f"❌ User creation failed: {response.status_code}")
            print(f"Response: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Error creating user: {e}")
        return None

def test_get_users():
    """Test getting all users."""
    print("\nTesting get users...")
    try:
        response = requests.get(f"{BASE_URL}/users/")
        if response.status_code == 200:
            users = response.json()
            print(f"✅ Retrieved {len(users)} users")
            return True
        else:
            print(f"❌ Get users failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error getting users: {e}")
        return False

def test_create_item(user_id):
    """Test creating an item."""
    print("\nTesting item creation...")
    item_data = {
        "title": "Test Item",
        "description": "This is a test item",
        "owner_id": user_id
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/items/",
            json=item_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 201:
            item = response.json()
            print(f"✅ Item created successfully: {item['title']}")
            return item['id']
        else:
            print(f"❌ Item creation failed: {response.status_code}")
            print(f"Response: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Error creating item: {e}")
        return None

def test_get_items():
    """Test getting all items."""
    print("\nTesting get items...")
    try:
        response = requests.get(f"{BASE_URL}/items/")
        if response.status_code == 200:
            items = response.json()
            print(f"✅ Retrieved {len(items)} items")
            return True
        else:
            print(f"❌ Get items failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error getting items: {e}")
        return False

def main():
    """Main test function."""
    print("🚀 Starting API tests...")
    print(f"Testing against: {BASE_URL}")
    
    # Test health endpoint
    if not test_health():
        print("\n❌ Health check failed. Make sure the server is running.")
        return
    
    # Test user operations
    user_id = test_create_user()
    if user_id:
        test_get_users()
        
        # Test item operations
        item_id = test_create_item(user_id)
        if item_id:
            test_get_items()
    
    print("\n🎉 API tests completed!")

if __name__ == "__main__":
    main() 
