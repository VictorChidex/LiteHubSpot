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
        todos = request.user.todos.all()
        serializer = TodoSerializer(todos, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = TodoCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        todo = serializer.save(user=request.user)
        return Response(TodoSerializer(todo).data, status=status.HTTP_201_CREATED)


class TodoDetailView(APIView):
    """Retrieve, update, and delete individual todos"""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk):
        todo = get_object_or_404(request.user.todos, pk=pk)
        return Response(TodoSerializer(todo).data)

    def put(self, request, pk):
        todo = get_object_or_404(request.user.todos, pk=pk)
        serializer = TodoUpdateSerializer(todo, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(TodoSerializer(todo).data)

    def delete(self, request, pk):
        todo = get_object_or_404(request.user.todos, pk=pk)
        todo.delete()
        return Response({'message': 'Todo deleted'}, status=status.HTTP_204_NO_CONTENT)


class TodoResolveView(APIView):
    """Toggle todo resolution status"""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        todo = get_object_or_404(request.user.todos, pk=pk)
        todo.resolved = not todo.resolved
        todo.save()
        return Response(TodoSerializer(todo).data)


class TodoStatusView(APIView):
    """Update todo status"""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        new_status = request.data.get('status')
        if new_status not in ['to_do', 'in_progress', 'done']:
            return Response({'error': 'Invalid status'}, status=status.HTTP_400_BAD_REQUEST)

        todo = get_object_or_404(request.user.todos, pk=pk)
        todo.status = new_status
        todo.save()
        return Response(TodoSerializer(todo).data)


class UserProfileView(APIView):
    """Get current user profile"""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        return Response(UserSerializer(request.user).data)
