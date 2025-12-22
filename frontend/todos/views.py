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
        return render(request, 'todos/index.html', {'todos': todos, 'user': user})

class TodoCreateView(AuthMixin, View):
    def post(self, request):
        user = self.get_user(request)
        title = request.POST.get('title')
        due_date = request.POST.get('due_date')
        description = request.POST.get('description', '')
        if title:
            MockBackendService.create_todo(user['id'], title, due_date, description)
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
            MockBackendService.update_todo(todo_id, title=title, due_date=due_date, description=description)
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
