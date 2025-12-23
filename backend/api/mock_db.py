"""
Mock database service for development and testing.
This provides in-memory storage that mimics a real database.
"""
from datetime import datetime
import uuid
from typing import Dict, List, Optional


class MockDatabase:
    """In-memory database simulation"""

    def __init__(self):
        self.users: Dict[str, Dict] = {}
        self.todos: Dict[str, Dict] = {}
        self.tokens: Dict[str, str] = {}  # token -> user_id

        # Create default admin user
        self._create_default_admin()

    def _create_default_admin(self):
        """Create default admin user for testing"""
        admin_data = {
            "id": str(uuid.uuid4()),
            "email": "admin@example.com",
            "username": "admin",
            "password": "password",
            "first_name": "",
            "last_name": "",
            "is_active": True,
            "date_joined": datetime.now().isoformat(),
        }
        self.users[admin_data["id"]] = admin_data

    # User operations
    def create_user(self, email: str, username: str, password: str,
                   first_name: str = "", last_name: str = "") -> Dict:
        """Create a new user"""
        # Check uniqueness
        for user in self.users.values():
            if user['email'] == email:
                raise ValueError("Email already registered")
            if user['username'] == username:
                raise ValueError("Username already taken")

        user_id = str(uuid.uuid4())
        user = {
            "id": user_id,
            "email": email,
            "username": username,
            "password": password,  # In real app, this would be hashed
            "first_name": first_name,
            "last_name": last_name,
            "is_active": True,
            "date_joined": datetime.now().isoformat(),
        }
        self.users[user_id] = user
        return user

    def get_user_by_id(self, user_id: str) -> Optional[Dict]:
        """Get user by ID"""
        return self.users.get(user_id)

    def get_user_by_email(self, email: str) -> Optional[Dict]:
        """Get user by email"""
        for user in self.users.values():
            if user['email'] == email:
                return user
        return None

    def get_user_by_username(self, username: str) -> Optional[Dict]:
        """Get user by username"""
        for user in self.users.values():
            if user['username'] == username:
                return user
        return None

    def authenticate_user(self, identifier: str, password: str) -> Optional[Dict]:
        """Authenticate user by email/username and password"""
        user = None

        # Try email first
        user = self.get_user_by_email(identifier)
        if not user:
            # Try username
            user = self.get_user_by_username(identifier)

        if user and user['password'] == password:  # In real app, check hash
            return user
        return None

    # Token operations
    def create_token(self, user_id: str) -> str:
        """Create authentication token for user"""
        token = str(uuid.uuid4())
        self.tokens[token] = user_id
        return token

    def get_user_by_token(self, token: str) -> Optional[Dict]:
        """Get user by authentication token"""
        user_id = self.tokens.get(token)
        if user_id:
            return self.get_user_by_id(user_id)
        return None

    def delete_token(self, token: str):
        """Delete authentication token"""
        self.tokens.pop(token, None)

    # Todo operations
    def create_todo(self, user_id: str, title: str, description: str = "",
                   due_date: str = None, priority: str = "normal",
                   status: str = "to_do") -> Dict:
        """Create a new todo"""
        todo_id = str(uuid.uuid4())
        todo = {
            "id": todo_id,
            "user_id": user_id,
            "title": title,
            "description": description,
            "due_date": due_date,
            "priority": priority,
            "status": status,
            "resolved": False,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
        }
        self.todos[todo_id] = todo
        return todo

    def get_todos_by_user(self, user_id: str) -> List[Dict]:
        """Get all todos for a user"""
        return [todo for todo in self.todos.values() if todo['user_id'] == user_id]

    def get_todo_by_id(self, todo_id: str) -> Optional[Dict]:
        """Get todo by ID"""
        return self.todos.get(todo_id)

    def update_todo(self, todo_id: str, **updates) -> Optional[Dict]:
        """Update todo with given fields"""
        todo = self.get_todo_by_id(todo_id)
        if not todo:
            return None

        # Update fields
        for key, value in updates.items():
            if key in todo:
                todo[key] = value

        todo['updated_at'] = datetime.now().isoformat()
        return todo

    def delete_todo(self, todo_id: str) -> bool:
        """Delete todo by ID"""
        if todo_id in self.todos:
            del self.todos[todo_id]
            return True
        return False

    def toggle_todo_resolution(self, todo_id: str) -> Optional[Dict]:
        """Toggle todo resolved status"""
        todo = self.get_todo_by_id(todo_id)
        if todo:
            todo['resolved'] = not todo['resolved']
            todo['updated_at'] = datetime.now().isoformat()
            return todo
        return None

    # Utility methods
    def clear_all(self):
        """Clear all data (for testing)"""
        self.users.clear()
        self.todos.clear()
        self.tokens.clear()
        self._create_default_admin()


# Global instance
mock_db = MockDatabase()