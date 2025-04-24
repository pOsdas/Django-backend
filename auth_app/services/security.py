import jwt
import redis
import bcrypt
import secrets
from django.conf import settings
from datetime import datetime, timezone, timedelta

from auth_app.config import pydantic_settings


# Подключение к Redis
redis_client = redis.Redis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    db=settings.REDIS_DB,
    decode_responses=settings.REDIS_DECODE_RESPONSES,
)


def encode_jwt(
    payload: dict,
    private_key: str = pydantic_settings.auth_jwt.private_key_path.read_text(),
    algorithm: str = pydantic_settings.auth_jwt.algorithm,
    expires_in: int = pydantic_settings.auth_jwt.access_token_expires_in,  # minutes
    expire_timedelta: timedelta | None = None,
):
    to_encode = payload.copy()
    now = datetime.now(timezone.utc)
    if expire_timedelta:
        expire = now + expire_timedelta
    else:
        expire = now + timedelta(minutes=expires_in)
    to_encode.update(exp=expire, iat=now)
    encoded = jwt.encode(to_encode, private_key, algorithm=algorithm)
    return encoded


def decode_jwt(
    token: str | bytes,
    public_key: str = pydantic_settings.auth_jwt.public_key_path.read_text(),
    algorithm: str = pydantic_settings.auth_jwt.algorithm,
):
    decoded = jwt.decode(token, public_key, algorithms=[algorithm])
    return decoded


def hash_password(password: str) -> bytes:
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode("utf-8"), salt)


def validate_password(password: str, hashed_password: bytes) -> bool:
    return bcrypt.checkpw(password.encode("utf-8"), hashed_password)


def verify_password(
        plain_password: str,
        hashed_password: bytes | memoryview
) -> bool:
    if isinstance(hashed_password, memoryview):
        hashed_password = hashed_password.tobytes()
    return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password)


def generate_static_auth_token() -> str:
    token = secrets.token_hex(16)
    return token
