from django.test import TestCase, Client
from django.urls import reverse
from .services import MockBackendService

class MockBackendServiceTests(TestCase):
    def setUp(self):
        # Reset mocks
        MockBackendService._users = {}
        MockBackendService._todos = {}

    def test_register_and_auth_user(self):
        MockBackendService.register_user('test@test.com', 'testuser', 'password123')
        
        # Auth with Email
        user1 = MockBackendService.authenticate_user('test@test.com', 'password123')
        self.assertIsNotNone(user1)
        self.assertEqual(user1['username'], 'testuser')

        # Auth with Username
        user2 = MockBackendService.authenticate_user('testuser', 'password123')
        self.assertIsNotNone(user2)
        self.assertEqual(user2['email'], 'test@test.com')
        
        # Test wrong password
        failed = MockBackendService.authenticate_user('testuser', 'wrong')
        self.assertIsNone(failed)

    def test_crud_todos(self):
        user = MockBackendService.register_user('user1@test.com', 'user1', 'pass')
        user_id = user['id']
        
        # Create
        todo = MockBackendService.create_todo(user_id, 'Test Task', '2025-01-01')
        self.assertEqual(todo['title'], 'Test Task')
        self.assertFalse(todo['resolved'])
        
        # Read
        todos = MockBackendService.get_todos(user_id)
        self.assertEqual(len(todos), 1)
        
        # Update
        updated = MockBackendService.update_todo(todo['id'], title='Updated Task', resolved=True)
        self.assertEqual(updated['title'], 'Updated Task')
        self.assertTrue(updated['resolved'])
        
        # Delete
        MockBackendService.delete_todo(todo['id'])
        todos = MockBackendService.get_todos(user_id)
        self.assertEqual(len(todos), 0)

class TodoViewsTests(TestCase):
    def setUp(self):
        MockBackendService._users = {}
        MockBackendService._todos = {}
        self.client = Client()
        # Register a user
        self.user = MockBackendService.register_user('viewuser@test.com', 'viewuser', 'pass')

    def login(self):
        # Simulate login by setting session directly since we mock auth
        session = self.client.session
        session['user_id'] = self.user['id']
        session['email'] = self.user['email']
        session['username'] = self.user['username']
        session.save()

    def test_redirect_if_not_logged_in(self):
        response = self.client.get(reverse('todo-list'))
        self.assertRedirects(response, reverse('login'))

    def test_login_view(self):
        # Login with username
        response = self.client.post(reverse('login'), {'identifier': 'viewuser', 'password': 'pass'})
        self.assertRedirects(response, reverse('todo-list'))
        
        # Login with email
        self.client.logout()
        response = self.client.post(reverse('login'), {'identifier': 'viewuser@test.com', 'password': 'pass'})
        self.assertRedirects(response, reverse('todo-list'))

    def test_create_todo(self):
        self.login()
        response = self.client.post(reverse('todo-create'), {
            'title': 'New Todo',
            'due_date': '2025-12-31'
        })
        self.assertRedirects(response, reverse('todo-list'))
        todos = MockBackendService.get_todos(self.user['id'])
        self.assertEqual(len(todos), 1)
        self.assertEqual(todos[0]['title'], 'New Todo')

    def test_interactivity(self):
        self.login()
        # Create
        MockBackendService.create_todo(self.user['id'], 'Task 1', '')
        t1 = MockBackendService.get_todos(self.user['id'])[0]
        
        # Resolve
        self.client.post(reverse('todo-resolve', args=[t1['id']]))
        t1 = MockBackendService.get_todo(t1['id'])
        self.assertTrue(t1['resolved'])
        
        # Delete
        self.client.post(reverse('todo-delete', args=[t1['id']]))
        todos = MockBackendService.get_todos(self.user['id'])
        self.assertEqual(len(todos), 0)
