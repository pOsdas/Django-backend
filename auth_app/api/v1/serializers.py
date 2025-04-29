from rest_framework import serializers


class AuthUserSerializer(serializers.Serializer):
    user_id = serializers.IntegerField()
    password = serializers.CharField()  # При необходимости преобразовать в Base64
    refresh_token = serializers.CharField(allow_null=True, required=False)
    updated_at = serializers.DateTimeField(allow_null=True, required=False)


class RegisterUserSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)
    email = serializers.EmailField()


class CombinedUserSerializer(serializers.Serializer):
    user_id = serializers.IntegerField()
    email = serializers.EmailField()


class TokenSerializer(serializers.Serializer):
    access_token = serializers.CharField()
    refresh_token = serializers.CharField(allow_null=True, required=False)
    token_type = serializers.CharField()


class RefreshSerializer(serializers.Serializer):
    refresh_token = serializers.CharField()
