from django.shortcuts import render, redirect
from django.views import View
from django.contrib import messages
from .services import MockBackendService

class AuthMixin:
    def get_user(self, request):
        user_id = request.session.get('user_id')
        if not user_id:
            return None
        return MockBackendService.get_user_by_id(user_id)

    def dispatch(self, request, *args, **kwargs):
        if not request.session.get('user_id'):
            return redirect('login')
        return super().dispatch(request, *args, **kwargs)

class SignupView(View):
    def get(self, request):
        return render(request, 'auth/signup.html')

    def post(self, request):
        data = request.POST
        email = data.get('email')
        username = data.get('username')
        password = data.get('password')
        
        try:
            MockBackendService.register_user(email, username, password)
            messages.success(request, "Account created! Please login.")
            return redirect('login')
        except ValueError as e:
            messages.error(request, str(e))
            return redirect('signup')

class LoginView(View):
    def get(self, request):
        return render(request, 'auth/login.html')

    def post(self, request):
        data = request.POST
        identifier = data.get('identifier')
        password = data.get('password')
        
        user = MockBackendService.authenticate_user(identifier, password)
        if user:
            request.session['user_id'] = user['id']
            request.session['email'] = user['email']
            request.session['username'] = user['username'] 
            return redirect('todo-list')
        else:
            messages.error(request, "Invalid credentials")
            return redirect('login')

class LogoutView(View):
    def get(self, request):
        request.session.flush()
        return redirect('login')

class TodoListView(AuthMixin, View):
    def get(self, request):
        user = self.get_user(request)
        todos = MockBackendService.get_todos(user['id'])
        view = request.GET.get('view', 'list')  # list or board
        
        # Prepare data for board view
        statuses = [
            ('to_do', 'To Do', 'gray'),
            ('in_progress', 'In Progress', 'blue'),
            ('done', 'Done', 'green')
        ]
        status_tasks = []
        for status, name, color in statuses:
            tasks = [todo for todo in todos if todo.get('status', 'to_do') == status]
            status_tasks.append((status, name, color, tasks))
        
        return render(request, 'todos/index.html', {
            'todos': todos, 
            'user': user, 
            'view': view,
            'status_tasks': status_tasks
        })

class TodoCreateView(AuthMixin, View):
    def post(self, request):
        user = self.get_user(request)
        title = request.POST.get('title')
        due_date = request.POST.get('due_date')
        description = request.POST.get('description', '')
        priority = request.POST.get('priority', 'medium')
        status = request.POST.get('status', 'to_do')
        if title:
            MockBackendService.create_todo(user['id'], title, due_date, description, priority, status)
            messages.success(request, "Todo created!")
        return redirect('todo-list')

class TodoUpdateView(AuthMixin, View):
    def post(self, request, todo_id):
        user = self.get_user(request)
        # Verify ownership implicitly by checking if todo exists and logic (though service mocked doesn't check owner strictly for update, we assume safety or add check)
        # For strictness:
        todo = MockBackendService.get_todo(todo_id)
        if todo and todo['user_id'] == user['id']:
            title = request.POST.get('title')
            due_date = request.POST.get('due_date')
            description = request.POST.get('description', '')
            priority = request.POST.get('priority', todo.get('priority', 'medium'))
            status = request.POST.get('status', todo.get('status', 'to_do'))
            MockBackendService.update_todo(todo_id, title=title, due_date=due_date, description=description, priority=priority, status=status)
        return redirect('todo-list')

class TodoDeleteView(AuthMixin, View):
    def post(self, request, todo_id):
        user = self.get_user(request)
        todo = MockBackendService.get_todo(todo_id)
        if todo and todo['user_id'] == user['id']:
            MockBackendService.delete_todo(todo_id)
        return redirect('todo-list')

class TodoResolveView(AuthMixin, View):
    def post(self, request, todo_id):
        user = self.get_user(request)
        todo = MockBackendService.get_todo(todo_id)
        if todo and todo['user_id'] == user['id']:
            # Toggle
            new_status = not todo['resolved']
            MockBackendService.update_todo(todo_id, resolved=new_status)
        return redirect('todo-list')

class TodoStatusView(AuthMixin, View):
    def post(self, request, todo_id):
        user = self.get_user(request)
        todo = MockBackendService.get_todo(todo_id)
        if todo and todo['user_id'] == user['id']:
            status = request.POST.get('status')
            if status in ['to_do', 'in_progress', 'done']:
                MockBackendService.update_todo(todo_id, status=status)
        return redirect('todo-list')
