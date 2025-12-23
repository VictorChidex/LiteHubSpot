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

    def test_register_duplicate_email(self):
        MockBackendService.register_user('test@test.com', 'testuser', 'password123')
        with self.assertRaises(ValueError):
            MockBackendService.register_user('test@test.com', 'differentuser', 'password123')

    def test_register_duplicate_username(self):
        MockBackendService.register_user('test@test.com', 'testuser', 'password123')
        with self.assertRaises(ValueError):
            MockBackendService.register_user('different@test.com', 'testuser', 'password123')

    def test_crud_todos(self):
        user = MockBackendService.register_user('user1@test.com', 'user1', 'pass')
        user_id = user['id']

        # Create
        todo = MockBackendService.create_todo(user_id, 'Test Task', '2025-01-01', 'My Description')
        self.assertEqual(todo['title'], 'Test Task')
        self.assertEqual(todo['description'], 'My Description')
        self.assertFalse(todo['resolved'])

        # Read
        todos = MockBackendService.get_todos(user_id)
        self.assertEqual(len(todos), 1)

        # Update
        updated = MockBackendService.update_todo(todo['id'], title='Updated Task', resolved=True, description='New Desc')
        self.assertEqual(updated['title'], 'Updated Task')
        self.assertEqual(updated['description'], 'New Desc')
        self.assertTrue(updated['resolved'])

        # Delete
        MockBackendService.delete_todo(todo['id'])
        todos = MockBackendService.get_todos(user_id)
        self.assertEqual(len(todos), 0)

    def test_todo_priorities_and_status(self):
        user = MockBackendService.register_user('user@test.com', 'user', 'pass')
        user_id = user['id']

        # Test all priority levels
        priorities = ['low', 'normal', 'high', 'urgent']
        for priority in priorities:
            todo = MockBackendService.create_todo(user_id, f'Task {priority}', '2025-01-01', '', priority)
            self.assertEqual(todo['priority'], priority)

        # Test all status levels
        statuses = ['to_do', 'in_progress', 'done']
        for status in statuses:
            todo = MockBackendService.create_todo(user_id, f'Task {status}', '2025-01-01', '', 'normal', status)
            self.assertEqual(todo['status'], status)

        todos = MockBackendService.get_todos(user_id)
        self.assertEqual(len(todos), 7)  # 4 priorities + 3 statuses

    def test_todo_default_values(self):
        user = MockBackendService.register_user('user@test.com', 'user', 'pass')
        user_id = user['id']

        # Create with minimal data
        todo = MockBackendService.create_todo(user_id, 'Minimal Task', '2025-01-01')
        self.assertEqual(todo['priority'], 'normal')  # Should be default
        self.assertEqual(todo['status'], 'to_do')  # Should be default
        self.assertEqual(todo['description'], '')  # Should be empty
        self.assertFalse(todo['resolved'])

    def test_user_isolation(self):
        # Create two users
        user1 = MockBackendService.register_user('user1@test.com', 'user1', 'pass')
        user2 = MockBackendService.register_user('user2@test.com', 'user2', 'pass')

        # Each creates a todo
        todo1 = MockBackendService.create_todo(user1['id'], 'User1 Task', '2025-01-01')
        todo2 = MockBackendService.create_todo(user2['id'], 'User2 Task', '2025-01-01')

        # Each should only see their own todos
        todos1 = MockBackendService.get_todos(user1['id'])
        todos2 = MockBackendService.get_todos(user2['id'])

        self.assertEqual(len(todos1), 1)
        self.assertEqual(len(todos2), 1)
        self.assertEqual(todos1[0]['title'], 'User1 Task')
        self.assertEqual(todos2[0]['title'], 'User2 Task')

class TodoViewsTests(TestCase):
    def setUp(self):
        MockBackendService._users = {}
        MockBackendService._todos = {}
        self.client = Client()
        # Register a user
        self.user = MockBackendService.register_user('viewuser@test.com', 'viewuser', 'pass')

    def login(self):
        # Perform real login since signed_cookies session backend makes direct manipulation diffcult in tests
        self.client.post(reverse('login'), {'identifier': 'viewuser', 'password': 'pass'})

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

    def test_signup_view(self):
        # Test GET request
        response = self.client.get(reverse('signup'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'auth/signup.html')

        # Test successful signup
        response = self.client.post(reverse('signup'), {
            'email': 'newuser@test.com',
            'username': 'newuser',
            'password': 'password123'
        })
        self.assertRedirects(response, reverse('login'))

        # Test duplicate email
        response = self.client.post(reverse('signup'), {
            'email': 'newuser@test.com',
            'username': 'differentuser',
            'password': 'password123'
        })
        self.assertRedirects(response, reverse('signup'))

    def test_logout_view(self):
        self.login()
        response = self.client.get(reverse('logout'))
        self.assertRedirects(response, reverse('login'))

        # Verify session is cleared
        response = self.client.get(reverse('todo-list'))
        self.assertRedirects(response, reverse('login'))

    def test_create_todo(self):
        self.login()
        response = self.client.post(reverse('todo-create'), {
            'title': 'New Todo',
            'due_date': '2025-12-31',
            'description': 'Details here'
        })
        self.assertRedirects(response, reverse('todo-list'))
        todos = MockBackendService.get_todos(self.user['id'])
        self.assertEqual(len(todos), 1)
        self.assertEqual(todos[0]['title'], 'New Todo')
        self.assertEqual(todos[0]['description'], 'Details here')

    def test_create_todo_with_priority_and_status(self):
        self.login()
        response = self.client.post(reverse('todo-create'), {
            'title': 'Priority Todo',
            'due_date': '2025-12-31',
            'description': 'High priority task',
            'priority': 'high',
            'status': 'in_progress'
        })
        self.assertRedirects(response, reverse('todo-list'))
        todos = MockBackendService.get_todos(self.user['id'])
        self.assertEqual(len(todos), 1)
        todo = todos[0]
        self.assertEqual(todo['priority'], 'high')
        self.assertEqual(todo['status'], 'in_progress')

    def test_create_todo_validation(self):
        self.login()
        # Test empty title
        response = self.client.post(reverse('todo-create'), {
            'title': '',
            'due_date': '2025-12-31'
        })
        self.assertRedirects(response, reverse('todo-list'))
        todos = MockBackendService.get_todos(self.user['id'])
        self.assertEqual(len(todos), 0)  # Should not create todo

    def test_todo_list_view(self):
        self.login()
        # Create some test todos
        MockBackendService.create_todo(self.user['id'], 'Task 1', '2025-01-01', 'Desc 1', 'urgent', 'to_do')
        MockBackendService.create_todo(self.user['id'], 'Task 2', '2025-01-02', 'Desc 2', 'normal', 'in_progress')
        MockBackendService.create_todo(self.user['id'], 'Task 3', '2025-01-03', 'Desc 3', 'low', 'done')

        # Test list view
        response = self.client.get(reverse('todo-list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'todos/index.html')
        self.assertEqual(len(response.context['todos']), 3)

        # Test board view
        response = self.client.get(reverse('todo-list') + '?view=board')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['view'], 'board')
        self.assertEqual(len(response.context['status_tasks']), 3)  # 3 status columns

    def test_update_todo(self):
        self.login()
        # Create a todo
        todo = MockBackendService.create_todo(self.user['id'], 'Original Task', '2025-01-01', 'Original desc', 'normal', 'to_do')

        # Update it
        response = self.client.post(reverse('todo-update', args=[todo['id']]), {
            'title': 'Updated Task',
            'due_date': '2025-12-31',
            'description': 'Updated description',
            'priority': 'urgent',
            'status': 'done'
        })
        self.assertRedirects(response, reverse('todo-list'))

        # Verify update
        updated_todo = MockBackendService.get_todo(todo['id'])
        self.assertEqual(updated_todo['title'], 'Updated Task')
        self.assertEqual(updated_todo['priority'], 'urgent')
        self.assertEqual(updated_todo['status'], 'done')

    def test_update_todo_ownership(self):
        self.login()
        # Create todo for current user
        todo = MockBackendService.create_todo(self.user['id'], 'My Task', '2025-01-01')

        # Create another user and try to update
        other_user = MockBackendService.register_user('other@test.com', 'other', 'pass')
        other_todo = MockBackendService.create_todo(other_user['id'], 'Other Task', '2025-01-01')

        # Try to update other user's todo (should not work due to ownership check)
        response = self.client.post(reverse('todo-update', args=[other_todo['id']]), {
            'title': 'Hacked Task',
            'due_date': '2025-01-01'
        })
        self.assertRedirects(response, reverse('todo-list'))

        # Verify other user's todo wasn't changed
        unchanged_todo = MockBackendService.get_todo(other_todo['id'])
        self.assertEqual(unchanged_todo['title'], 'Other Task')

    def test_delete_todo(self):
        self.login()
        # Create and delete a todo
        todo = MockBackendService.create_todo(self.user['id'], 'Task to Delete', '2025-01-01')

        response = self.client.post(reverse('todo-delete', args=[todo['id']]))
        self.assertRedirects(response, reverse('todo-list'))

        # Verify deletion
        todos = MockBackendService.get_todos(self.user['id'])
        self.assertEqual(len(todos), 0)

    def test_resolve_todo(self):
        self.login()
        # Create a todo
        todo = MockBackendService.create_todo(self.user['id'], 'Task to Resolve', '2025-01-01')

        # Resolve it
        response = self.client.post(reverse('todo-resolve', args=[todo['id']]))
        self.assertRedirects(response, reverse('todo-list'))

        # Verify resolved
        updated_todo = MockBackendService.get_todo(todo['id'])
        self.assertTrue(updated_todo['resolved'])

        # Resolve again (should toggle back)
        response = self.client.post(reverse('todo-resolve', args=[todo['id']]))
        updated_todo = MockBackendService.get_todo(todo['id'])
        self.assertFalse(updated_todo['resolved'])

    def test_status_update(self):
        self.login()
        # Create a todo
        todo = MockBackendService.create_todo(self.user['id'], 'Status Test', '2025-01-01', '', 'normal', 'to_do')

        # Update status to in_progress
        response = self.client.post(reverse('todo-status', args=[todo['id']]), {'status': 'in_progress'})
        self.assertRedirects(response, reverse('todo-list'))

        updated_todo = MockBackendService.get_todo(todo['id'])
        self.assertEqual(updated_todo['status'], 'in_progress')

        # Update status to done
        response = self.client.post(reverse('todo-status', args=[todo['id']]), {'status': 'done'})
        updated_todo = MockBackendService.get_todo(todo['id'])
        self.assertEqual(updated_todo['status'], 'done')

    def test_invalid_status_update(self):
        self.login()
        todo = MockBackendService.create_todo(self.user['id'], 'Status Test', '2025-01-01')

        # Try invalid status
        response = self.client.post(reverse('todo-status', args=[todo['id']]), {'status': 'invalid_status'})
        self.assertRedirects(response, reverse('todo-list'))

        # Status should remain unchanged
        updated_todo = MockBackendService.get_todo(todo['id'])
        self.assertEqual(updated_todo['status'], 'to_do')  # Default status

    def test_priority_levels_in_ui(self):
        """Test that all priority levels work correctly in the UI"""
        self.login()

        priorities = ['low', 'normal', 'high', 'urgent']
        for priority in priorities:
            response = self.client.post(reverse('todo-create'), {
                'title': f'{priority.title()} Priority Task',
                'due_date': '2025-12-31',
                'priority': priority
            })
            self.assertRedirects(response, reverse('todo-list'))

        todos = MockBackendService.get_todos(self.user['id'])
        self.assertEqual(len(todos), 4)

        # Verify all priorities are set correctly
        todo_priorities = [todo['priority'] for todo in todos]
        for priority in priorities:
            self.assertIn(priority, todo_priorities)

    def test_board_view_status_grouping(self):
        """Test that board view correctly groups todos by status"""
        self.login()

        # Create todos with different statuses
        MockBackendService.create_todo(self.user['id'], 'Todo Task', '2025-01-01', '', 'normal', 'to_do')
        MockBackendService.create_todo(self.user['id'], 'In Progress Task', '2025-01-02', '', 'high', 'in_progress')
        MockBackendService.create_todo(self.user['id'], 'Done Task', '2025-01-03', '', 'low', 'done')

        response = self.client.get(reverse('todo-list') + '?view=board')
        self.assertEqual(response.status_code, 200)

        status_tasks = response.context['status_tasks']
        self.assertEqual(len(status_tasks), 3)  # 3 status columns

        # Check each status column
        for status, name, color, tasks in status_tasks:
            if status == 'to_do':
                self.assertEqual(len(tasks), 1)
                self.assertEqual(tasks[0]['title'], 'Todo Task')
            elif status == 'in_progress':
                self.assertEqual(len(tasks), 1)
                self.assertEqual(tasks[0]['title'], 'In Progress Task')
            elif status == 'done':
                self.assertEqual(len(tasks), 1)
                self.assertEqual(tasks[0]['title'], 'Done Task')
