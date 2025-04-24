import uuid
from django.conf import settings
from django.core.cache import cache

SESSION_PREFIX = "session:"
SESSION_TTL = getattr(settings, "SESSION_TTL", 60 * 60 * 24 * 7)


def create_session(user_id: int) -> str:
    token = uuid.uuid4().hex
    cache_key = SESSION_PREFIX + token
    cache.set(cache_key, {"user_id": user_id}, timeout=SESSION_TTL)
    return token


def get_session(token: str) -> dict | None:
    return cache.get(SESSION_PREFIX + token)
