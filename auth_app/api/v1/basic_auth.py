import httpx
import logging
import redis
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, exceptions
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.authentication import BasicAuthentication
from rest_framework.permissions import AllowAny, IsAuthenticated

from auth_app import crud
from auth_app.models import AuthUser
# from auth_app.api.core.mixins import AsyncAPIView
from auth_app.config import pydantic_settings as settings
from .serializers import RegisterUserSerializer, AuthUserSerializer
from auth_app.services.security import verify_password, hash_password

# Настраиваем logger
logger = logging.getLogger(__name__)

# Подключение к Redis
redis_client = redis.Redis(host="localhost", port=6379, db=0, decode_responses=True)

# failed attempts
MAX_ATTEMPTS = 5
BLOCK_TIME_SECONDS = 300  # 5 минут


class BasicAuthCredentialsAPIView(APIView):
    authentication_classes = [BasicAuthentication]
    permission_classes = [AllowAny]

    def get(self, request):
        user = request.user
        return Response({
            "message": "Hi!",
            "username": user.username if user and hasattr(user, "username") else "Anonymous",
            "password": request.META.get("HTTP_AUTHORIZATION", "")
        })


class RegisterUserAPIView(APIView):
    serializer_class = RegisterUserSerializer
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterUserSerializer(data=request.data)
        if not serializer.is_valid():
            logger.warning(f"Validation error: {serializer.errors}")
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST,
            )
        user_data = serializer.validated_data

        # 1 Запрос на создание
        try:
            with httpx.Client(timeout=10.0) as client:
                response = client.post(
                    f"{settings.user_service_url}/api/v1/users/create_user/",
                    json={
                        "username": user_data["username"],
                        "email": user_data["email"],
                    }
                )
                response.raise_for_status()
                user_id = response.json().get("user_id")

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
            new_auth_user = AuthUser.objects.create(
                user_id=user_id,
                password=hashed_pw,
                refresh_token=None,
            )
        except Exception as exc:
            logger.error(f"Auth user creation failed: {str(exc)}")
            return Response(
                {"detail": "Internal server error"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        return Response(
            {
                "message": "User registered successfully",
                "user_id": user_id
            },
            status=status.HTTP_201_CREATED
        )


class GetUsersAPIView(APIView):
    # permission_classes = [IsAuthenticated]
    permission_classes = [AllowAny]
    serializer = AuthUserSerializer
    authentication_classes = []

    def get(self, request):
        try:
            users = crud.get_all_users()
            if not users:
                return Response(
                    {"detail": "Users not found"},
                    status=status.HTTP_404_NOT_FOUND
                )

            serializer = AuthUserSerializer(users, many=True)
            return Response(serializer.data)

        except Exception as exc:
            logger.error(f"Error while fetching users: {str(exc)}")
            return Response(
                {"detail": "Internal server error"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


# Вспомогательная асинхронная функция для аутентификации по basic auth
def get_auth_user_username(request):
    auth = BasicAuthentication()
    auth_tuple = auth.authenticate(request=request)
    if auth_tuple is None:
        raise exceptions.AuthenticationFailed("Invalid username or password")
    try:
        user, _ = auth_tuple
        username = user.username
    except exceptions.AuthenticationFailed:
        raise exceptions.AuthenticationFailed("Invalid username or password")

    unauthed_exc = exceptions.AuthenticationFailed(
        "Invalid username or password",
    )

    # Проверка попыток входа через redis
    key = f"failed_attempts:{username}"
    attempts = redis_client.get(key)
    attempts = int(attempts) if attempts else 0

    if attempts >= MAX_ATTEMPTS:
        raise exceptions.PermissionDenied(
            "Too many failed attempts, try again later"
        )

    # Запрос пользователя из user_service
    with httpx.Client(timeout=10.0) as client:
        response = client.get(
            f"{settings.user_service_url}/api/v1/users/username/{username}/"
        )

    if response.status_code != 200:
        redis_client.incr(key)
        redis_client.expire(key, BLOCK_TIME_SECONDS)
        raise unauthed_exc  # Пользователь не найден

    user_data = response.json()
    user_id = user_data.get("id")
    is_active = user_data.get("is_active")

    if not user_id or not is_active:
        redis_client.incr(key)
        redis_client.expire(key, BLOCK_TIME_SECONDS)
        raise unauthed_exc

    try:
        auth_user = AuthUser.objects.get(user_id=user_id)
    except ObjectDoesNotExist:
        redis_client.incr(key)
        redis_client.expire(key, BLOCK_TIME_SECONDS)
        raise unauthed_exc

    hashed_password = auth_user.password

    # secrets
    req_password = request.query_params.get("password") or request.data.get("password", "")
    if not verify_password(req_password, hashed_password):
        redis_client.incr(key)
        redis_client.expire(key, BLOCK_TIME_SECONDS)
        raise unauthed_exc

    redis_client.delete(key)
    return username


class BasicAuthUsernameAPIView(APIView):
    authentication_classes = [BasicAuthentication]
    permission_classes = [AllowAny]

    def get(self, request):
        username = get_auth_user_username(request)
        return Response({
            "username": username
        })


def get_username_by_static_auth_token(request):
    static_token = request.headers.get("x-auth-token")
    if static_token and (username := crud.static_auth_token_to_user_id.get(static_token)):
        return username
    raise exceptions.AuthenticationFailed("Invalid token")


class CheckTokenAuthAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        username = get_username_by_static_auth_token(request)
        return Response({
            "message": f"Hi!, {username}!",
            "username": username,
        })


class DeleteAuthUserAPIView(APIView):
    def delete(self, request, user_id: int):
        try:
            crud.delete_auth_user(user_id)
        except ObjectDoesNotExist:
            return Response(
                {"detail": f"User with {user_id} not found in auth_service"},
                status=status.HTTP_404_NOT_FOUND
            )
        return Response({"message": "Auth user deleted"})
        # try:
        #     crud.get_auth_user(user_id)
        # except ObjectDoesNotExist:
        #     return Response(
        #         {"detail": f"User with {user_id} not found in auth_service"},
        #         status=status.HTTP_404_NOT_FOUND
        #     )
        # crud.delete_auth_user(user_id)
        # return Response({"message": "Auth user deleted"})
