from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from .sqlalchemy_db import init_db, SessionLocal
from .sql_models import Todo as SQLTodo

User = get_user_model()

class TodoAPITests(APITestCase):
    def setUp(self):
        # Ensure User table exists (Django auth)
        self.user_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'testpassword123'
        }
        self.user = User.objects.create_user(**self.user_data)
        
        # Ensure SQL tables exist
        init_db()
        
        # Get token
        url = reverse('api:login')
        response = self.client.post(url, {
            'identifier': self.user_data['username'],
            'password': self.user_data['password']
        })
        self.token = response.data['token']
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token)

    def test_create_todo(self):
        """
        Ensure we can create a new todo object.
        """
        url = reverse('api:todo-list')
        data = {'title': 'Test Todo', 'priority': 'high'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['title'], 'Test Todo')
        self.assertEqual(response.data['priority'], 'high')

    def test_get_todos(self):
        """
        Ensure we can list todos.
        """
        # Create a todo first
        url = reverse('api:todo-list')
        self.client.post(url, {'title': 'Test Todo 1'}, format='json')
        
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # We expect at least 1 todo (plus any seeded ones if the test db isn't flushed, 
        # but Django tests usually flush the DB. However, our SQL storage is separate.
        # Ideally, we should mock the DB session or ensure isolation, but for this task
        # we'll check if the created one is in the list)
        self.assertTrue(len(response.data) >= 1)
        self.assertEqual(response.data[-1]['title'], 'Test Todo 1')

    def tearDown(self):
        # Clean up SQL data created during test
        # Since we use a persistent SQLite file or shared DB, we should be careful.
        # But for this simple app, we might just leave it or try to delete what we made.
        # A better approach for tests would be using an in-memory SQLite DB for SQLAlchemy,
        # but that requires refactoring `sqlalchemy_db.py` to be test-aware.
        # For now, we will manually delete the todos created by this user.
        db = SessionLocal()
        try:
            db.query(SQLTodo).filter(SQLTodo.user_id == self.user.id).delete()
            db.commit()
        finally:
            db.close()
