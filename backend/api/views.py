from rest_framework import status, generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token
from django.contrib.auth import login, logout
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from .mock_db import mock_db
from .serializers import (
    UserSerializer, LoginSerializer, TodoSerializer,
    TodoCreateSerializer, TodoUpdateSerializer, StatusUpdateSerializer
)


class APIRootView(APIView):
    """API root endpoint showing available endpoints"""
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        return Response({
            "message": "Welcome to LiteHubSpot API",
            "version": "1.0",
            "endpoints": {
                "authentication": {
                    "signup": "/api/auth/signup/",
                    "login": "/api/auth/login/",
                    "logout": "/api/auth/logout/",
                    "profile": "/api/auth/profile/"
                },
                "todos": {
                    "list": "/api/todos/",
                    "detail": "/api/todos/<uuid>/",
                    "resolve": "/api/todos/<uuid>/resolve/",
                    "status": "/api/todos/<uuid>/status/"
                }
            }
        })


class SignupView(APIView):
    """User registration endpoint"""
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        try:
            user = mock_db.create_user(
                email=request.data.get('email'),
                username=request.data.get('username'),
                password=request.data.get('password'),
                first_name=request.data.get('first_name', ''),
                last_name=request.data.get('last_name', '')
            )
            token = mock_db.create_token(user['id'])
            return Response({
                'user': user,
                'token': token,
                'message': 'User created successfully'
            }, status=status.HTTP_201_CREATED)
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': 'Registration failed'}, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    """User login endpoint"""
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        identifier = request.data.get('identifier')
        password = request.data.get('password')

        user = mock_db.authenticate_user(identifier, password)
        if user:
            token = mock_db.create_token(user['id'])
            return Response({
                'user': user,
                'token': token,
                'message': 'Login successful'
            })
        return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)


class LogoutView(APIView):
    """User logout endpoint"""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        # For mock DB, we don't need to do anything special
        return Response({'message': 'Logout successful'})


class TodoListView(APIView):
    """List and create todos"""
    permission_classes = [permissions.AllowAny]  # Using mock auth

    def get(self, request):
        # For simplicity, using a mock user ID from header or default
        user_id = request.headers.get('X-User-ID', 'default-admin-id')
        todos = mock_db.get_todos_by_user(user_id)
        return Response(todos)

    def post(self, request):
        user_id = request.headers.get('X-User-ID', 'default-admin-id')

        try:
            todo = mock_db.create_todo(
                user_id=user_id,
                title=request.data.get('title'),
                description=request.data.get('description', ''),
                due_date=request.data.get('due_date'),
                priority=request.data.get('priority', 'normal'),
                status=request.data.get('status', 'to_do')
            )
            return Response(todo, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class TodoDetailView(APIView):
    """Retrieve, update, and delete individual todos"""
    permission_classes = [permissions.AllowAny]  # Using mock auth

    def get(self, request, pk):
        todo = mock_db.get_todo_by_id(str(pk))
        if not todo:
            return Response({'error': 'Todo not found'}, status=status.HTTP_404_NOT_FOUND)
        return Response(todo)

    def put(self, request, pk):
        todo = mock_db.get_todo_by_id(str(pk))
        if not todo:
            return Response({'error': 'Todo not found'}, status=status.HTTP_404_NOT_FOUND)

        # Update allowed fields
        updates = {}
        allowed_fields = ['title', 'description', 'due_date', 'priority', 'status', 'resolved']
        for field in allowed_fields:
            if field in request.data:
                updates[field] = request.data[field]

        updated_todo = mock_db.update_todo(str(pk), **updates)
        if updated_todo:
            return Response(updated_todo)
        return Response({'error': 'Update failed'}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        success = mock_db.delete_todo(str(pk))
        if success:
            return Response({'message': 'Todo deleted'}, status=status.HTTP_204_NO_CONTENT)
        return Response({'error': 'Todo not found'}, status=status.HTTP_404_NOT_FOUND)


class TodoResolveView(APIView):
    """Toggle todo resolution status"""
    permission_classes = [permissions.AllowAny]  # Using mock auth

    def post(self, request, pk):
        todo = mock_db.toggle_todo_resolution(str(pk))
        if todo:
            return Response(todo)
        return Response({'error': 'Todo not found'}, status=status.HTTP_404_NOT_FOUND)


class TodoStatusView(APIView):
    """Update todo status"""
    permission_classes = [permissions.AllowAny]  # Using mock auth

    def post(self, request, pk):
        new_status = request.data.get('status')
        if new_status not in ['to_do', 'in_progress', 'done']:
            return Response({'error': 'Invalid status'}, status=status.HTTP_400_BAD_REQUEST)

        updated_todo = mock_db.update_todo(str(pk), status=new_status)
        if updated_todo:
            return Response(updated_todo)
        return Response({'error': 'Todo not found'}, status=status.HTTP_404_NOT_FOUND)


class UserProfileView(APIView):
    """Get current user profile"""
    permission_classes = [permissions.AllowAny]  # Using mock auth

    def get(self, request):
        user_id = request.headers.get('X-User-ID', 'default-admin-id')
        user = mock_db.get_user_by_id(user_id)
        if user:
            return Response(user)
        return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
