import httpx
from rest_framework import status
from django.db import IntegrityError
from rest_framework.views import APIView
from rest_framework.response import Response
from django.core.exceptions import ObjectDoesNotExist

from user_app.config import pydantic_settings as settings
from user_app.crud import (
    get_all_users, get_user_by_id, get_user_by_email,
    create_user, delete_user, get_user_by_username
)
from user_app.api.v1.serializers import CreateUser, ReadUser, UserSerializer, UserUpdateSerializer


# from .utils.fake_db import fake_users_db


class CreateUserAPIView(APIView):
    # permission_classes = [AllowAny]
    async def post(self, request, *args, **kwargs):
        serializer = CreateUser(data=request.data)
        if not serializer.is_valid():
            return Response(
                {"details": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Проверяем существует ли пользователь с таким email
        email = serializer.validated_data.get("email")
        try:
            exiting_user = await get_user_by_email(email=email)
            if exiting_user:
                return Response(
                    {"detail": "User with such email already exists"},
                    status=status.HTTP_409_CONFLICT,
                )
        except ObjectDoesNotExist:
            existing_user = None

        # Создаём пользователя
        try:
            user = await create_user(**serializer.validated_data)
        except IntegrityError as e:
            return Response(
                {"detail": f"Integrity error: {str(e)}"},
                status=status.HTTP_409_CONFLICT,
            )
        except Exception as e:
            return Response(
                {"detail": "Internal server error: " + str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        read_serializer = ReadUser(user=user)
        return Response(read_serializer.data, status=status.HTTP_201_CREATED)


class GetUsersAPIView(APIView):
    async def get(self, request, *args, **kwargs):
        users = await get_all_users()
        serializer = ReadUser(users, many=True)
        return Response(serializer.data)


class GetUserAPIView(APIView):
    async def get(self, user_id, *args, **kwargs):
        try:
            user = await get_user_by_id(user_id=user_id)
        except ObjectDoesNotExist:
            return Response(
                {"detail": "User not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        serializer = UserSerializer(user)
        return Response(serializer.data)


class GetUserByUsernameAPIView(APIView):
    async def get(self, username, *args, **kwargs):
        try:
            user = await get_user_by_username(username=username)
        except ObjectDoesNotExist:
            return Response(
                {"detail": "User not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = UserSerializer(user)
        return Response(serializer.data)


class UpdateUserAPIView(APIView):
    async def patch(self, request, user_id, *args, **kwargs):
        serializer = UserUpdateSerializer(data=request.data, partial=True)
        if not serializer.is_valid():
            return Response(
                {"detail": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            user = await get_user_by_id(user_id=user_id)
        except ObjectDoesNotExist:
            return Response(
                {"detail": "User not found"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        updated = False

        if 'new_name' in serializer.validated_data:
            user.username = serializer.validated_data["new_name"]
            updated = True
        if 'email' in serializer.validated_data:
            user.email = serializer.validated_data["email"]
            updated = True
        if 'is_active' in serializer.validated_data:
            user.is_active = serializer.validated_data["is_active"]
            updated = True

        if not updated:
            return Response(
                {"detail": "No data provided for update"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            await user.asave()
        except Exception as e:
            return Response(
                {"detail": f"Internal server error {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
        serializer = UserUpdateSerializer(user)
        return Response(serializer.data)


class DeleteUserAPIView(APIView):
    async def delete(self, request, user_id, *args, **kwargs):
        try:
            user = await get_user_by_id(user_id=user_id)
            # Делаем запрос к auth_app
            async with httpx.AsyncClient() as client:
                response = await client.delete(f"{settings.auth_service_url}/api/v1/auth/{user.user_id}")

            # Пользователь не найден
            if response.status_code != 200:
                return Response(
                    {"detail": "Invalid username"},
                    status=status.HTTP_401_UNAUTHORIZED,
                )

            # Пользователь найден
            try:
                await delete_user(user_id=user.user_id)
            except Exception as e:
                return Response(
                    {"detail": f"Internal server error: {str(e)}"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )

            return Response(
                {"message": "User deleted successfully", "id": user_id},
                status=status.HTTP_200_OK,
            )

        except ObjectDoesNotExist:
            return Response(
                {"detail": "User not found"},
                status=status.HTTP_404_NOT_FOUND
            )
