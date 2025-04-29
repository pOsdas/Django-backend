import uuid
import redis
from django.conf import settings
from django.core.cache import cache

from auth_app.redis_client import redis_client

SESSION_PREFIX = "session:"
SESSION_TTL = getattr(settings, "SESSION_TTL", 60 * 60 * 24 * 7)


def create_session(user_id: int) -> str:
    token = uuid.uuid4().hex
    key = SESSION_PREFIX + token
    redis_client.set(key, user_id, ex=SESSION_TTL)
    return token


def get_session(token: str) -> int | None:
    key = SESSION_PREFIX + token
    user_id: int = redis_client.get(key)
    if user_id is not None:
        # продлеваем жизнь сессии (можете убрать)
        redis_client.expire(key, SESSION_TTL)
        return user_id
    return None


def delete_session(token: str) -> None:
    key = SESSION_PREFIX + token
    redis_client.delete(key)
