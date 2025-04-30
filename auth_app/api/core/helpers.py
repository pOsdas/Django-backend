from datetime import timedelta

from auth_app.services import security
from auth_app.config import pydantic_settings


TOKEN_TYPE_FIELD = "type"
ACCESS_TOKEN_TYPE = "access"
REFRESH_TOKEN_TYPE = "refresh"


def create_jwt(
        token_type: str,
        token_data: dict,
        expires_in: int = pydantic_settings.auth_jwt.access_token_expires_in,
        expire_timedelta: timedelta | None = None,
) -> str:
    jwt_payload = {TOKEN_TYPE_FIELD: token_type}
    jwt_payload.update(token_data)
    return security.encode_jwt(
        payload=jwt_payload,
        expires_in=expires_in,
        expire_timedelta=expire_timedelta,
    )


def create_access_token(user_id, email) -> str:
    jwt_payload = {
        # subject
        "sub": user_id,
        "user_id": user_id,
        "email": email,
    }

    return create_jwt(
        token_type=ACCESS_TOKEN_TYPE,
        token_data=jwt_payload,
        expires_in=pydantic_settings.auth_jwt.access_token_expires_in,
    )


def create_refresh_token(user_id, email) -> str:
    jwt_payload = {
        "sub": user_id,
        "email": email,
    }
    return create_jwt(
        token_type=REFRESH_TOKEN_TYPE,
        token_data=jwt_payload,
        expire_timedelta=timedelta(days=pydantic_settings.auth_jwt.refresh_token_expires_days),
    )