from rest_framework import status, generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token
from rest_framework.renderers import JSONRenderer, TemplateHTMLRenderer, BrowsableAPIRenderer
from django.contrib.auth import authenticate, get_user_model
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from .serializers import (
    UserSerializer, UserCreateSerializer, LoginSerializer, TodoSerializer,
    TodoCreateSerializer, TodoUpdateSerializer, StatusUpdateSerializer
)


User = get_user_model()

# Initialize SQLAlchemy DB and import models
from .sqlalchemy_db import init_db, SessionLocal
from .sql_models import Todo as SQLTodo

init_db()

class APIRootView(APIView):
    """API root endpoint showing available endpoints"""
    permission_classes = [permissions.AllowAny]
    renderer_classes = [JSONRenderer, TemplateHTMLRenderer, BrowsableAPIRenderer]

    def get(self, request):
        from django.urls import reverse

        # Build absolute URLs using reverse where possible. For detail routes
        # include a `{uuid}` placeholder (curly braces) to avoid JSON escaping
        # of angle brackets and to make copy/paste friendly.
        auth_signup = request.build_absolute_uri(reverse('api:signup'))
        auth_login = request.build_absolute_uri(reverse('api:login'))
        auth_logout = request.build_absolute_uri(reverse('api:logout'))
        auth_profile = request.build_absolute_uri(reverse('api:profile'))

        todos_list = request.build_absolute_uri(reverse('api:todo-list'))

        context = {
            "message": "Welcome to LiteHubSpot API",
            "version": "1.0",
            "endpoints": {
                "authentication": {
                    "signup": auth_signup,
                    "login": auth_login,
                    "logout": auth_logout,
                    "profile": auth_profile,
                },
                "todos": {
                    "list": todos_list,
                    "detail": todos_list + "{uuid}/",
                    "resolve": todos_list + "{uuid}/resolve/",
                    "status": todos_list + "{uuid}/status/",
                }
            }
        }

        # If the client prefers HTML, render a template with the context.
        # TemplateHTMLRenderer will be used when the request's Accept header
        # includes text/html (e.g., a browser).
        if isinstance(request.accepted_renderer, TemplateHTMLRenderer):
            return Response(context, template_name='api/root.html')

        return Response(context)


class SignupView(APIView):
    """User registration endpoint"""
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = UserCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        token, _ = Token.objects.get_or_create(user=user)
        return Response({
            'user': UserSerializer(user).data,
            'token': token.key,
            'message': 'User created successfully'
        }, status=status.HTTP_201_CREATED)


class LoginView(APIView):
    """User login endpoint"""
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, _ = Token.objects.get_or_create(user=user)
        return Response({'user': UserSerializer(user).data, 'token': token.key, 'message': 'Login successful'})


class LogoutView(APIView):
    """User logout endpoint"""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        # Delete token to logout
        if hasattr(request, 'auth') and request.auth:
            request.auth.delete()
        return Response({'message': 'Logout successful'})


class TodoListView(APIView):
    """List and create todos"""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        db = SessionLocal()
        try:
            rows = db.query(SQLTodo).filter(SQLTodo.user_id == request.user.id).all()
            data = [r.to_dict(user_obj={'id': request.user.id, 'email': request.user.email, 'username': request.user.username}) for r in rows]
            return Response(data)
        finally:
            db.close()

    def post(self, request):
        # Validate minimal required field
        title = request.data.get('title')
        if not title:
            return Response({'error': 'title is required'}, status=status.HTTP_400_BAD_REQUEST)

        db = SessionLocal()
        try:
            todo = SQLTodo(
                user_id=request.user.id,
                title=title,
                description=request.data.get('description', ''),
                due_date=request.data.get('due_date'),
                due_time=request.data.get('due_time'),
                start_date=request.data.get('start_date'),
                priority=request.data.get('priority', 'normal'),
                status=request.data.get('status', 'to_do')
            )
            db.add(todo)
            db.commit()
            db.refresh(todo)
            return Response(todo.to_dict(user_obj={'id': request.user.id, 'email': request.user.email, 'username': request.user.username}), status=status.HTTP_201_CREATED)
        finally:
            db.close()


class TodoDetailView(APIView):
    """Retrieve, update, and delete individual todos"""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk):
        db = SessionLocal()
        try:
            todo = db.query(SQLTodo).filter(SQLTodo.id == pk, SQLTodo.user_id == request.user.id).first()
            if not todo:
                return Response({'detail': 'Not found.'}, status=status.HTTP_404_NOT_FOUND)
            return Response(todo.to_dict(user_obj={'id': request.user.id, 'email': request.user.email, 'username': request.user.username}))
        finally:
            db.close()

    def put(self, request, pk):
        db = SessionLocal()
        try:
            todo = db.query(SQLTodo).filter(SQLTodo.id == pk, SQLTodo.user_id == request.user.id).first()
            if not todo:
                return Response({'detail': 'Not found.'}, status=status.HTTP_404_NOT_FOUND)
            for field in ['title', 'description', 'due_date', 'due_time', 'start_date', 'priority', 'status', 'resolved']:
                if field in request.data:
                    setattr(todo, field, request.data.get(field))
            db.add(todo)
            db.commit()
            db.refresh(todo)
            return Response(todo.to_dict(user_obj={'id': request.user.id, 'email': request.user.email, 'username': request.user.username}))
        finally:
            db.close()

    def delete(self, request, pk):
        db = SessionLocal()
        try:
            todo = db.query(SQLTodo).filter(SQLTodo.id == pk, SQLTodo.user_id == request.user.id).first()
            if not todo:
                return Response({'detail': 'Not found.'}, status=status.HTTP_404_NOT_FOUND)
            db.delete(todo)
            db.commit()
            return Response({'message': 'Todo deleted'}, status=status.HTTP_204_NO_CONTENT)
        finally:
            db.close()


class TodoResolveView(APIView):
    """Toggle todo resolution status"""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        db = SessionLocal()
        try:
            todo = db.query(SQLTodo).filter(SQLTodo.id == pk, SQLTodo.user_id == request.user.id).first()
            if not todo:
                return Response({'detail': 'Not found.'}, status=status.HTTP_404_NOT_FOUND)
            todo.resolved = not todo.resolved
            db.add(todo)
            db.commit()
            db.refresh(todo)
            return Response(todo.to_dict(user_obj={'id': request.user.id, 'email': request.user.email, 'username': request.user.username}))
        finally:
            db.close()


class TodoStatusView(APIView):
    """Update todo status"""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        new_status = request.data.get('status')
        if new_status not in ['to_do', 'in_progress', 'done']:
            return Response({'error': 'Invalid status'}, status=status.HTTP_400_BAD_REQUEST)
        db = SessionLocal()
        try:
            todo = db.query(SQLTodo).filter(SQLTodo.id == pk, SQLTodo.user_id == request.user.id).first()
            if not todo:
                return Response({'detail': 'Not found.'}, status=status.HTTP_404_NOT_FOUND)
            todo.status = new_status
            db.add(todo)
            db.commit()
            db.refresh(todo)
            return Response(todo.to_dict(user_obj={'id': request.user.id, 'email': request.user.email, 'username': request.user.username}))
        finally:
            db.close()


class UserProfileView(APIView):
    """Get current user profile"""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        return Response(UserSerializer(request.user).data)
