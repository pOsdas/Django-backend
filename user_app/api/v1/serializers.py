from rest_framework import serializers

from user_app.models import User


class CreateUser(serializers.Serializer):
    username = serializers.CharField(min_length=3, max_length=32)
    email = serializers.EmailField(max_length=255)


class ReadUser(serializers.Serializer):
    class Meta:
        model = User
        fields = ['user_id', 'username', 'email']


class UserSerializer(serializers.Serializer):
    class Meta:
        model = User
        fields = ['user_id', 'username', 'email', 'is_active', 'created_at', 'updated_at']
        read_only_fields = ['user_id', 'created_at', 'updated_at']


class UserUpdateSerializer(serializers.Serializer):
    new_name = serializers.CharField(min_length=3, max_length=32, required=False)
    email = serializers.EmailField(required=False)
    is_active = serializers.BooleanField(required=False)
