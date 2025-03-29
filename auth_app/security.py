import jwt
import bcrypt
from datetime import datetime, timezone, timedelta
from passlib.context import CryptContext
from django.conf import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def encode_jwt(
    payload: dict,
    private_key: str = settings.AUTH_JWT['private_key_path'].read_text(),
    algorithm: str = settings.AUTH_JWT['algorithm'],
    expires_in: int = settings.AUTH_JWT['access_token_expires_in'],  # minutes
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
    public_key: str = settings.AUTH_JWT['public_key_path'].read_text(),
    algorithm: str = settings.AUTH_JWT['algorithm'],
):
    decoded = jwt.decode(token, public_key, algorithms=[algorithm])
    return decoded


def hash_password(password: str) -> bytes:
    salt = bcrypt.gensalt()
    pwd_bytes = password.encode("utf-8")
    return bcrypt.hashpw(pwd_bytes, salt)


def validate_password(password: str, hashed_password: bytes) -> bool:
    return bcrypt.checkpw(password.encode("utf-8"), hashed_password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)
