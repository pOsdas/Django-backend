import redis
import httpx
from rest_framework import exceptions

from auth_app.config import pydantic_settings as settings

redis_client = redis.Redis(host="localhost", port=6379, db=0, decode_responses=True)


# ---- tokens ----
def store_static_token(
        token: str,
        user_id: int,
        ttl: int = 3600
) -> None:
    redis_client.set(f"static_auth_token:{token}", user_id, ex=ttl)


def get_user_id_by_static_auth_token(token: str) -> int | None:
    user_id: str = redis_client.get(f"static_auth_token:{token}")
    return int(user_id) if user_id else None


def get_username_by_static_auth_token(request):
    token = request.headers.get("x-auth-token")
    if not token:
        raise exceptions.AuthenticationFailed("Missing token")

    user_id = get_user_id_by_static_auth_token(token)
    if not user_id:
        raise exceptions.AuthenticationFailed("Invalid token")

    # Запрос к user_service
    with httpx.Client(timeout=5.0) as client:
        response = client.get(
            f"{settings.user_service_url}/api/v1/users/{user_id}/"
        )

    if response.status_code != 200:
        raise exceptions.AuthenticationFailed("User not found")

    user_data = response.json()
    return user_data["username"]