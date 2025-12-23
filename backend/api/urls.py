from django.urls import path
from . import views

app_name = 'api'

urlpatterns = [
    # API root
    path('', views.APIRootView.as_view(), name='api-root'),

    # Authentication endpoints
    path('auth/signup/', views.SignupView.as_view(), name='signup'),
    path('auth/login/', views.LoginView.as_view(), name='login'),
    path('auth/logout/', views.LogoutView.as_view(), name='logout'),

    # User profile
    path('auth/profile/', views.UserProfileView.as_view(), name='profile'),

    # Todo endpoints
    path('todos/', views.TodoListView.as_view(), name='todo-list'),
    path('todos/<uuid:pk>/', views.TodoDetailView.as_view(), name='todo-detail'),
    path('todos/<uuid:pk>/resolve/', views.TodoResolveView.as_view(), name='todo-resolve'),
    path('todos/<uuid:pk>/status/', views.TodoStatusView.as_view(), name='todo-status'),
]