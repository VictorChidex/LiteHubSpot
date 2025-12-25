from django.test import TestCase, Client
from django.urls import reverse
from unittest.mock import patch
from django.conf import settings
from django.contrib.sessions.backends.signed_cookies import SessionStore

class TodoViewTests(TestCase):
    def setUp(self):
        self.client = Client()

    @patch('todos.views.services.get_todos')
    @patch('todos.views.services.get_user_by_token')
    def test_index_view_authenticated(self, mock_get_user, mock_get_todos):
        # Create a signed session manually
        session = SessionStore()
        session['auth_token'] = 'fake-token'
        session['username'] = 'testuser'
        session.save()
        
        # Set the cookie
        self.client.cookies[settings.SESSION_COOKIE_NAME] = session.session_key

        # Mock service responses
        mock_get_user.return_value = {'username': 'testuser', 'email': 'test@example.com'}
        mock_get_todos.return_value = [
            {'id': '1', 'title': 'Test Task', 'status': 'to_do', 'priority': 'high', 'due_date': '2025-01-01'}
        ]

        response = self.client.get(reverse('todo-list'))
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Task')
        self.assertContains(response, 'testuser')

    def test_index_view_redirects_if_no_token(self):
        # No token in session
        response = self.client.get(reverse('todo-list'))
        # Should redirect to login
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith(reverse('login')))
