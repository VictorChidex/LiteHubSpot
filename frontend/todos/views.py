from django.shortcuts import render, redirect
from django.views import View
from django.contrib import messages
from . import services


class AuthMixin:
    def get_user(self, request):
        token = request.session.get('auth_token')
        if not token:
            return None
        return services.get_user_by_token(token)

    def dispatch(self, request, *args, **kwargs):
        if not request.session.get('auth_token'):
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
            services.register_user(email, username, password)
            messages.success(request, "Account created! Please login.")
            return redirect('login')
        except Exception as e:
            messages.error(request, str(e))
            return redirect('signup')


class LoginView(View):
    def get(self, request):
        return render(request, 'auth/login.html')

    def post(self, request):
        data = request.POST
        identifier = data.get('identifier')
        password = data.get('password')

        resp = services.authenticate_user(identifier, password)
        if resp and resp.get('token'):
            token = resp['token']
            request.session['auth_token'] = token
            user = resp.get('user')
            if user:
                request.session['username'] = user.get('username')
                request.session['email'] = user.get('email')
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
        token = request.session.get('auth_token')
        todos = services.get_todos(token)
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
            'user': self.get_user(request),
            'view': view,
            'status_tasks': status_tasks
        })


class TodoCreateView(AuthMixin, View):
    def post(self, request):
        token = request.session.get('auth_token')
        title = request.POST.get('title')
        due_date = request.POST.get('due_date')
        due_time = request.POST.get('due_time')
        description = request.POST.get('description', '')
        priority = request.POST.get('priority', 'medium')
        status = request.POST.get('status', 'to_do')
        if title:
            services.create_todo(None, title, due_date, due_time, description, priority, status, token=token)
            messages.success(request, "Todo created!")
        return redirect('todo-list')


class TodoUpdateView(AuthMixin, View):
    def post(self, request, todo_id):
        token = request.session.get('auth_token')
        todo = services.get_todo(todo_id, token)
        user = self.get_user(request)
        if todo and user and todo.get('user') and todo['user'].get('id') == user.get('id'):
            title = request.POST.get('title')
            due_date = request.POST.get('due_date')
            due_time = request.POST.get('due_time')
            description = request.POST.get('description', '')
            priority = request.POST.get('priority', todo.get('priority', 'medium'))
            status = request.POST.get('status', todo.get('status', 'to_do'))
            services.update_todo(todo_id, title=title, due_date=due_date, due_time=due_time, description=description, priority=priority, status=status, token=token)
        return redirect('todo-list')


class TodoDeleteView(AuthMixin, View):
    def post(self, request, todo_id):
        token = request.session.get('auth_token')
        todo = services.get_todo(todo_id, token)
        user = self.get_user(request)
        if todo and user and todo.get('user') and todo['user'].get('id') == user.get('id'):
            services.delete_todo(todo_id, token=token)
        return redirect('todo-list')


class TodoResolveView(AuthMixin, View):
    def post(self, request, todo_id):
        token = request.session.get('auth_token')
        todo = services.get_todo(todo_id, token)
        user = self.get_user(request)
        if todo and user and todo.get('user') and todo['user'].get('id') == user.get('id'):
            new_resolved = not todo.get('resolved', False)
            services.update_todo(todo_id, resolved=new_resolved, token=token)
        return redirect('todo-list')


class TodoStatusView(AuthMixin, View):
    def post(self, request, todo_id):
        token = request.session.get('auth_token')
        todo = services.get_todo(todo_id, token)
        user = self.get_user(request)
        if todo and user and todo.get('user') and todo['user'].get('id') == user.get('id'):
            status = request.POST.get('status')
            if status in ['to_do', 'in_progress', 'done']:
                services.update_todo(todo_id, status=status, token=token)
        return redirect('todo-list')
