from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls), # Optional, keeping it std but we don't use it much with mock
    path('', include('todos.urls')),
]
