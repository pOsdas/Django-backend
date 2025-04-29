"""
create
read
update
delete
"""
import json
import httpx
from typing import Sequence, Optional
from django.core.exceptions import ObjectDoesNotExist

from auth_app.config import pydantic_settings
from auth_app.models import AuthUser
from auth_app.redis_client import redis_client


# ---- users ----
def get_all_users() -> Sequence[AuthUser]:
    return list(AuthUser.objects.order_by("user_id"))


def get_auth_user(
        user_id: int,
) -> Optional[AuthUser]:
    try:
        user = AuthUser.objects.get(user_id=user_id)
        return user
    except ObjectDoesNotExist:
        raise


def get_user_service_user_by_id(user_id: int):
    with httpx.Client(timeout=10.0) as client:
        response = client.get(
            f"{pydantic_settings.user_service_url}/api/v1/users/{user_id}/"
        )
        response.raise_for_status()

    return response.json()


def get_user_service_user_by_username(username: str):
    with httpx.Client(timeout=10.0) as client:
        response = client.get(
            f"{pydantic_settings.user_service_url}/api/v1/users/username/{username}/"
        )
        response.raise_for_status()

    return response.json()


def delete_auth_user_redis_data(user) -> None:
    user_id = user.user_id
    user_data = get_user_service_user_by_id(user_id)
    username = user_data.get("username")

    # Удаляем счетчик неудачных попыток
    redis_client.delete(f"failed_attempts:{username}")

    # Удаляем все сессии, связанные с user_id
    for key in redis_client.scan_iter("session:*"):
        try:
            session_data = redis_client.get(key)
            if not session_data:
                continue

            parsed = json.loads(session_data)
            if parsed.get("user_id") == user_id:
                redis_client.delete(key)

        except (json.JSONDecodeError, TypeError) as e:
            continue


def delete_auth_user(
        user_id: int,
) -> None:
    user = get_auth_user(user_id)
    if user:
        delete_auth_user_redis_data(user)  # чистим redis
        user.delete()
