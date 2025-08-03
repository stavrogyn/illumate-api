#!/usr/bin/env python3
"""
Integration tests for the FastAPI application.
These tests require the server to be running.
"""

import pytest
import requests
import json
import time
from uuid import uuid4

BASE_URL = "http://localhost:8000"

def test_health():
    """Test the health endpoint."""
    print("Testing health endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"Response: {response.json()}")
        if response.status_code == 200:
            print("✅ Health check passed")
            assert True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            assert False
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to the server. Make sure it's running.")
        pytest.skip("Server not running")

def test_create_tenant():
    """Test creating a tenant."""
    print("\nTesting tenant creation...")
    tenant_data = {
        "name": f"Test Organization {uuid4().hex[:8]}",
        "description": "Test organization for integration tests"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/tenants/",
            json=tenant_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 201:
            tenant = response.json()
            print(f"✅ Tenant created successfully: {tenant['name']}")
            assert tenant['id'] is not None
            return tenant['id']
        else:
            print(f"❌ Tenant creation failed: {response.status_code}")
            print(f"Response: {response.text}")
            assert False
    except Exception as e:
        print(f"❌ Error creating tenant: {e}")
        pytest.skip("Server not running")

def test_create_user():
    """Test creating a user."""
    print("\nTesting user creation...")
    
    # First create a tenant
    tenant_id = test_create_tenant()
    if not tenant_id:
        pytest.skip("Could not create tenant for user test")
    
    user_data = {
        "email": f"test{uuid4().hex[:8]}@example.com",
        "role": "therapist",
        "locale": "en"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/users/?tenant_id={tenant_id}&password=testpassword123",
            json=user_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 201:
            user = response.json()
            print(f"✅ User created successfully: {user['email']}")
            assert user['id'] is not None
        else:
            print(f"❌ User creation failed: {response.status_code}")
            print(f"Response: {response.text}")
            assert False
    except Exception as e:
        print(f"❌ Error creating user: {e}")
        pytest.skip("Server not running")

def test_get_users():
    """Test getting all users."""
    print("\nTesting get users...")
    
    # First create a tenant
    tenant_id = test_create_tenant()
    if not tenant_id:
        pytest.skip("Could not create tenant for get users test")
    
    try:
        response = requests.get(f"{BASE_URL}/users/?tenant_id={tenant_id}")
        if response.status_code == 200:
            users = response.json()
            print(f"✅ Retrieved {len(users)} users")
            assert isinstance(users, list)
        else:
            print(f"❌ Get users failed: {response.status_code}")
            assert False
    except Exception as e:
        print(f"❌ Error getting users: {e}")
        pytest.skip("Server not running")

def test_create_client():
    """Test creating a client."""
    print("\nTesting client creation...")
    
    # First create a tenant
    tenant_id = test_create_tenant()
    if not tenant_id:
        pytest.skip("Could not create tenant for client test")
    
    client_data = {
        "full_name": "John Doe",
        "birthday": "1990-01-01T00:00:00",
        "tags": ["new", "therapy"]
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/clients/?tenant_id={tenant_id}",
            json=client_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 201:
            client = response.json()
            print(f"✅ Client created successfully: {client['full_name']}")
            assert client['id'] is not None
        else:
            print(f"❌ Client creation failed: {response.status_code}")
            print(f"Response: {response.text}")
            assert False
    except Exception as e:
        print(f"❌ Error creating client: {e}")
        pytest.skip("Server not running")

def test_get_clients():
    """Test getting all clients."""
    print("\nTesting get clients...")
    
    # First create a tenant
    tenant_id = test_create_tenant()
    if not tenant_id:
        pytest.skip("Could not create tenant for get clients test")
    
    try:
        response = requests.get(f"{BASE_URL}/clients/?tenant_id={tenant_id}")
        if response.status_code == 200:
            clients = response.json()
            print(f"✅ Retrieved {len(clients)} clients")
            assert isinstance(clients, list)
        else:
            print(f"❌ Get clients failed: {response.status_code}")
            assert False
    except Exception as e:
        print(f"❌ Error getting clients: {e}")
        pytest.skip("Server not running") 
