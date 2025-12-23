#!/usr/bin/env python3
"""
Test script to verify the API is running
"""
import requests
import json

BASE_URL = "http://127.0.0.1:8001/api"

def test_api():
    """Test basic API endpoints"""
    print("Testing API endpoints...")

    # Test signup
    signup_data = {
        "email": "test@example.com",
        "username": "testuser",
        "password": "testpass"
    }

    try:
        response = requests.post(f"{BASE_URL}/auth/signup/", json=signup_data)
        if response.status_code == 201:
            print("✓ Signup endpoint working")
            user_data = response.json()
            token = user_data.get('token')
        else:
            print(f"✗ Signup failed: {response.status_code} - {response.text}")
            return
    except Exception as e:
        print(f"✗ Could not connect to API: {e}")
        return

    # Test login
    login_data = {
        "identifier": "test@example.com",
        "password": "testpass"
    }

    try:
        response = requests.post(f"{BASE_URL}/auth/login/", json=login_data)
        if response.status_code == 200:
            print("✓ Login endpoint working")
        else:
            print(f"✗ Login failed: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"✗ Login error: {e}")

    # Test create todo
    headers = {"Authorization": f"Token {token}"}
    todo_data = {
        "title": "Test Todo",
        "description": "Testing the API",
        "priority": "high"
    }

    try:
        response = requests.post(f"{BASE_URL}/todos/", json=todo_data, headers=headers)
        if response.status_code == 201:
            print("✓ Todo creation working")
            todo = response.json()
        else:
            print(f"✗ Todo creation failed: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"✗ Todo creation error: {e}")

    print("API test completed!")

if __name__ == "__main__":
    test_api()