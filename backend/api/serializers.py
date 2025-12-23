from rest_framework import serializers
from .mock_db import mock_db


class UserSerializer(serializers.Serializer):
    """Serializer for user data"""
    id = serializers.CharField(read_only=True)
    email = serializers.EmailField()
    username = serializers.CharField()
    first_name = serializers.CharField(required=False, allow_blank=True)
    last_name = serializers.CharField(required=False, allow_blank=True)
    date_joined = serializers.DateTimeField(read_only=True)


class LoginSerializer(serializers.Serializer):
    """Serializer for login data"""
    identifier = serializers.CharField()  # email or username
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        identifier = data.get('identifier')
        password = data.get('password')

        user = mock_db.authenticate_user(identifier, password)
        if not user:
            raise serializers.ValidationError('Invalid credentials')

        data['user'] = user
        return data


class TodoSerializer(serializers.Serializer):
    """Serializer for todo data"""
    id = serializers.CharField(read_only=True)
    title = serializers.CharField(max_length=200)
    description = serializers.CharField(required=False, allow_blank=True)
    due_date = serializers.DateTimeField(required=False, allow_null=True)
    priority = serializers.ChoiceField(choices=['low', 'normal', 'high'], default='normal')
    status = serializers.ChoiceField(choices=['to_do', 'in_progress', 'done'], default='to_do')
    resolved = serializers.BooleanField(default=False)
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)
    user_id = serializers.CharField(read_only=True)


class TodoCreateSerializer(serializers.Serializer):
    """Serializer for creating todos"""
    title = serializers.CharField(max_length=200)
    description = serializers.CharField(required=False, allow_blank=True)
    due_date = serializers.DateTimeField(required=False, allow_null=True)
    priority = serializers.ChoiceField(choices=['low', 'normal', 'high'], default='normal')
    status = serializers.ChoiceField(choices=['to_do', 'in_progress', 'done'], default='to_do')


class TodoUpdateSerializer(serializers.Serializer):
    """Serializer for updating todos"""
    title = serializers.CharField(max_length=200, required=False)
    description = serializers.CharField(required=False, allow_blank=True)
    due_date = serializers.DateTimeField(required=False, allow_null=True)
    priority = serializers.ChoiceField(choices=['low', 'normal', 'high'], required=False)
    status = serializers.ChoiceField(choices=['to_do', 'in_progress', 'done'], required=False)
    resolved = serializers.BooleanField(required=False)


class StatusUpdateSerializer(serializers.Serializer):
    """Serializer for updating todo status"""
    status = serializers.ChoiceField(choices=['to_do', 'in_progress', 'done'])