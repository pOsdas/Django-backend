"""
create
read
update
delete
"""
from rest_framework import status
from django.db import IntegrityError
from typing import Sequence, Optional
from rest_framework.response import Response
from django.core.exceptions import ObjectDoesNotExist, ValidationError


from user_app.models import User
from user_app.api.v1.serializers import CreateUser


async def get_all_users() -> Sequence[User]:
    users = [user async for user in User.objects.order_by("user_id")]
    return users


async def get_user_by_id(
        user_id: int
) -> Optional[User]:
    try:
        user = await User.objects.aget(user_id=user_id)
        return user
    except ObjectDoesNotExist:
        return None


async def get_user_by_username(
        username: str
) -> Optional[User]:
    try:
        user = await User.objects.aget(username=username)
        return user
    except ObjectDoesNotExist:
        return None


async def get_user_by_email(
        email: str,
) -> Optional[User]:
    try:
        result = await User.objects.aget(email=email)
        return result
    except ObjectDoesNotExist:
        return None


async def create_user(
        user_create: CreateUser,
) -> User | Response:
    try:
        user = await User.objects.acreate(**user_create.dict())
        return user
    except IntegrityError:
        # Например, email уже существует
        return Response(
            {"detail": "Пользователь с таким email уже существует"},
            status=status.HTTP_409_CONFLICT,
        )
    except ValidationError:
        return Response(
            {"detail": f"Ошибка валидации"},
            status=status.HTTP_422_UNPROCESSABLE_ENTITY,
        )


async def delete_user(
        user_id: int,
) -> Response | dict:
    user = await get_user_by_id(user_id=user_id)
    if user:
        try:
            await user.adelete()
        except ObjectDoesNotExist:
            return Response(
                {"detail": "Failed to delete user"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    if not user:
        return Response(
            {"detail": "User not found"},
            status=status.HTTP_404_NOT_FOUND,
        )

    return {"message": "User deleted successfully", "id": id}
