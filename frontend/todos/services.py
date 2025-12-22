from datetime import datetime
import uuid

class MockBackendService:
    _users = {
        "admin@example.com": {
            "id": "default-admin-id",
            "email": "admin@example.com",
            "username": "admin",
            "password": "password"
        }
    }
    _todos = {}  # {id: {id, user_id, title, due_date, resolved}}
    
    @classmethod
    def register_user(cls, email, username, password):
        # Check uniqueness
        for user in cls._users.values():
            if user['email'] == email:
                raise ValueError("Email already registered")
            if user['username'] == username:
                raise ValueError("Username already taken")
                
        user_id = str(uuid.uuid4())
        user = {
            "id": user_id,
            "email": email,
            "username": username,
            "password": password
        }
        cls._users[email] = user
        return user

    @classmethod
    def authenticate_user(cls, identifier, password):
        # identifier can be email or username
        found_user = None
        for user in cls._users.values():
            if user['email'] == identifier or user['username'] == identifier:
                found_user = user
                break
        
        if found_user and found_user["password"] == password:
            return found_user
        return None

    @classmethod
    def get_user_by_id(cls, user_id):
        for user in cls._users.values():
            if user["id"] == user_id:
                return user
        return None

    @classmethod
    def get_todos(cls, user_id):
        return [todo for todo in cls._todos.values() if todo["user_id"] == user_id]

    @classmethod
    def create_todo(cls, user_id, title, due_date):
        todo_id = str(uuid.uuid4())
        todo = {
            "id": todo_id,
            "user_id": user_id,
            "title": title,
            "due_date": due_date,
            "resolved": False
        }
        cls._todos[todo_id] = todo
        return todo

    @classmethod
    def get_todo(cls, todo_id):
        return cls._todos.get(todo_id)

    @classmethod
    def update_todo(cls, todo_id, **kwargs):
        todo = cls._todos.get(todo_id)
        if not todo:
            return None
        todo.update(kwargs)
        return todo

    @classmethod
    def delete_todo(cls, todo_id):
        if todo_id in cls._todos:
            del cls._todos[todo_id]
            return True
        return False
