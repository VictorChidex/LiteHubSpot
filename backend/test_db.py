#!/usr/bin/env python3
"""
Test script for the mock database
"""
import sys
import os

# Add the backend directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from api.mock_db import mock_db

def test_mock_database():
    """Test basic mock database operations"""
    print("Testing Mock Database...")

    # Test creating a user
    try:
        user = mock_db.create_user(
            email="test@example.com",
            username="testuser",
            password="testpass",
            first_name="Test",
            last_name="User"
        )
        print(f"✓ Created user: {user['email']}")
    except Exception as e:
        print(f"✗ Failed to create user: {e}")
        return

    # Test authentication
    try:
        auth_user = mock_db.authenticate_user("test@example.com", "testpass")
        if auth_user:
            print(f"✓ Authentication successful for: {auth_user['email']}")
        else:
            print("✗ Authentication failed")
    except Exception as e:
        print(f"✗ Authentication error: {e}")

    # Test creating a todo
    try:
        todo = mock_db.create_todo(
            user_id=user['id'],
            title="Test Todo",
            description="This is a test todo",
            priority="high"
        )
        print(f"✓ Created todo: {todo['title']}")
    except Exception as e:
        print(f"✗ Failed to create todo: {e}")

    # Test getting todos
    try:
        todos = mock_db.get_todos_by_user(user['id'])
        print(f"✓ Retrieved {len(todos)} todos for user")
    except Exception as e:
        print(f"✗ Failed to get todos: {e}")

    # Test updating todo
    try:
        updated_todo = mock_db.update_todo(
            todo_id=todo['id'],
            title="Updated Test Todo",
            status="done"
        )
        print(f"✓ Updated todo: {updated_todo['title']} - {updated_todo['status']}")
    except Exception as e:
        print(f"✗ Failed to update todo: {e}")

    print("Mock database test completed!")

if __name__ == "__main__":
    test_mock_database()