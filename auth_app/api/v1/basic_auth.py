import httpx
import logging
import base64
import binascii
from django.http import JsonResponse
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, exceptions
from drf_spectacular.utils import extend_schema
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.authentication import BasicAuthentication
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken

from auth_app.models import AuthUser
from auth_app.config import pydantic_settings
from auth_app.redis_client import redis_client
# from auth_app.api.core.mixins import AsyncAPIView
from auth_app.crud import user_crud, tokens_crud, session_crud
from .serializers import RegisterUserSerializer, AuthUserSerializer
from auth_app.api.core.helpers import create_access_token, create_refresh_token
from auth_app.services.security import (
    verify_password, hash_password,
    generate_static_auth_token
)

# Настраиваем logger
logger = logging.getLogger(__name__)

MAX_ATTEMPTS = settings.AUTH_MAX_ATTEMPTS
BLOCK_TIME = settings.AUTH_BLOCK_TIME_SECONDS


@extend_schema(tags=["Basic Authentication"])
class BasicAuthCredentialsAPIView(APIView):
    """
    Не для продакшена.
    """
    authentication_classes = [BasicAuthentication]
    permission_classes = [AllowAny]

    def get(self, request):
        user = request.user
        return Response({
            "message": "Hi!",
            "username": user.username if user and hasattr(user, "username") else "Anonymous",
            "password": request.META.get("HTTP_AUTHORIZATION", "")
        })


@extend_schema(tags=["Register"])
class RegisterUserAPIView(APIView):
    """
    Регистрируем пользователя, \n
    Выдаем пользователю access и refresh tokens, \n
    Выдаем ему x-auth-token.
    """
    serializer_class = RegisterUserSerializer
    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request):
        serializer = RegisterUserSerializer(data=request.data)
        if not serializer.is_valid():
            logger.warning(f"Validation error: {serializer.errors}")
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST,
            )
        user_data = serializer.validated_data
        email = user_data["email"]

        # 1 Запрос на создание
        username = user_data["username"]
        try:
            response = user_crud.create_user_service_user( username, email)
            user_id = response.get("user_id")
            if not user_id:
                raise ValueError("Missing user ID in response")

        except (httpx.HTTPError, ValueError) as exc:
            logger.error(f"User service error: {str(exc)}")
            return Response(
                {"detail": "Failed to create user profile in user_service"},
                status=status.HTTP_502_BAD_GATEWAY,
            )

        # 2 Хешируем пароль и создаем запись в auth_service
        try:
            hashed_pw = hash_password(user_data["password"])
            refresh = create_refresh_token(user_id, email)
            AuthUser.objects.create(
                user_id=user_id,
                password=hashed_pw,
                refresh_token=refresh,
            )
        except Exception as exc:
            logger.error(f"Auth user creation failed: {str(exc)}")
            return Response(
                {"detail": "Internal server error"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        token = generate_static_auth_token()
        tokens_crud.store_static_token(token, user_id)
        access = create_access_token(user_id, email)

        return Response(
            {
                "message": "User registered successfully",
                "user_id": user_id,
                "x-auth-token": token,
                "access": access,
            },
            status=status.HTTP_201_CREATED
        )


# Вспомогательная асинхронная функция для аутентификации по username/password
def get_auth_user_username(request):
    # Парсим basic заголовок
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.lower().startswith("basic "):
        raise exceptions.AuthenticationFailed("Missing basic auth header")

    token = auth_header.split(" ", 1)[1].strip()
    try:
        decoded = base64.b64decode(token).decode("utf-8")
        username, password = decoded.split(":", 1)
    except (binascii.Error, ValueError):
        raise exceptions.AuthenticationFailed("Invalid basic auth header")

    unauthed_exc = exceptions.AuthenticationFailed(
        "Invalid username or password",
    )

    # Проверка попыток входа через redis
    key = f"failed_attempts:{username}"
    attempts: int = redis_client.get(key)
    attempts = int(attempts) if attempts else 0

    if attempts >= MAX_ATTEMPTS:
        raise exceptions.PermissionDenied(
            "Too many failed attempts, try again later"
        )

    # Запрос пользователя из user_service
    try:
        response = user_crud.get_user_service_user_by_username(username)
    except httpx.HTTPStatusError:
        # Сбрасываем счётчик на ошибки сети
        redis_client.incr(key)
        redis_client.expire(key, BLOCK_TIME)
        raise unauthed_exc

    user_id = response.get("user_id")
    is_active = response.get("is_active")

    if not user_id or not is_active:
        redis_client.incr(key)
        redis_client.expire(key, BLOCK_TIME)
        raise unauthed_exc

    try:
        auth_user = AuthUser.objects.get(user_id=user_id)
    except ObjectDoesNotExist:
        redis_client.incr(key)
        redis_client.expire(key, BLOCK_TIME)
        raise unauthed_exc

    # secrets
    if not verify_password(password, auth_user.password):
        redis_client.incr(key)
        redis_client.expire(key, BLOCK_TIME)
        raise unauthed_exc

    redis_client.delete(key)
    return username, user_id


@extend_schema(tags=["Basic Authentication"])
class BasicAuthUsernameAPIView(APIView):
    """
    Login через username и password
    """
    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request):
        username, user_id = get_auth_user_username(request)

        # x-auth-token
        session_token = session_crud.create_session(user_id)

        # access and refresh tokens
        user_data = user_crud.get_user_service_user_by_username(username=username)
        email = user_data.get("email")
        access_token = create_access_token(user_id, email)
        refresh_token = create_refresh_token(user_id, email)
        auth_user = AuthUser.objects.get(user_id=user_id)
        auth_user.refresh_token = refresh_token
        auth_user.save()

        response = JsonResponse({
            "user_id": user_id,
            "username": username,
            "session_id": session_token,  # x-auth-token
            "access_token": access_token  # по сути тот же x-auth-token
        })
        response.set_cookie(
            key="cookie_session_id",
            value=session_token,
            httponly=True,  # # javascript protection
            samesite="Lax",  # CSRF protection
            max_age=settings.COOKIE_SESSION_TTL,
        )
        return response


@extend_schema(tags=["Basic Authentication"])
class CheckTokenAuthAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        username = tokens_crud.get_username_by_static_auth_token(request)
        return Response({
            "message": f"Hi!, {username}!",
            "username": username,
        })
