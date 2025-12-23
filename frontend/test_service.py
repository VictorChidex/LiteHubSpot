#!/usr/bin/env python3
"""
Test script for the frontend mock service
"""
import sys
import os

# Add the frontend directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'frontend'))

from todos.services import MockBackendService

def test_mock_service():
    """Test basic mock service operations"""
    print("Testing Frontend Mock Service...")

    # Clear any existing data
    MockBackendService._todos = {}

    # Test registering a user
    try:
        user = MockBackendService.register_user(
            email="test@example.com",
            username="testuser",
            password="testpass"
        )
        print(f"✓ Registered user: {user['email']}")
    except Exception as e:
        print(f"✗ Failed to register user: {e}")
        return

    # Test authentication
    try:
        auth_user = MockBackendService.authenticate_user("test@example.com", "testpass")
        if auth_user:
            print(f"✓ Authentication successful for: {auth_user['email']}")
        else:
            print("✗ Authentication failed")
    except Exception as e:
        print(f"✗ Authentication error: {e}")

    # Test creating a todo
    try:
        todo = MockBackendService.create_todo(
            user_id=user['id'],
            title="Test Todo",
            due_date="2024-12-31",
            description="This is a test todo"
        )
        print(f"✓ Created todo: {todo['title']}")
    except Exception as e:
        print(f"✗ Failed to create todo: {e}")
        return

    # Test getting todos
    try:
        todos = MockBackendService.get_todos(user['id'])
        print(f"✓ Retrieved {len(todos)} todos for user")
    except Exception as e:
        print(f"✗ Failed to get todos: {e}")

    # Test updating todo
    try:
        updated_todo = MockBackendService.update_todo(
            todo_id=todo['id'],
            title="Updated Test Todo",
            resolved=True
        )
        print(f"✓ Updated todo: {updated_todo['title']} - resolved: {updated_todo['resolved']}")
    except Exception as e:
        print(f"✗ Failed to update todo: {e}")

    print("Frontend mock service test completed!")

if __name__ == "__main__":
    test_mock_service()