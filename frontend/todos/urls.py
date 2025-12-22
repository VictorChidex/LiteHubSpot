from django.urls import path
from . import views

urlpatterns = [
    path('signup/', views.SignupView.as_view(), name='signup'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    
    path('', views.TodoListView.as_view(), name='todo-list'),
    path('create/', views.TodoCreateView.as_view(), name='todo-create'),
    path('update/<str:todo_id>/', views.TodoUpdateView.as_view(), name='todo-update'),
    path('delete/<str:todo_id>/', views.TodoDeleteView.as_view(), name='todo-delete'),
    path('resolve/<str:todo_id>/', views.TodoResolveView.as_view(), name='todo-resolve'),
]
