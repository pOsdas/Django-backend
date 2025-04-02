import os
from pathlib import Path
from dotenv import load_dotenv
from pydantic import BaseModel, PostgresDsn
from pydantic_settings import BaseSettings, SettingsConfigDict

# Принудительно загружаем .env и .env-template
load_dotenv()


BASE_DIR = Path(__file__).resolve().parent
CERTS_DIR = BASE_DIR / "certs"


class RunModel(BaseModel):
    host: str = "127.0.0.1"
    port: int = 8005


class ApiV1Prefix(BaseModel):
    prefix: str = "/v1"
    auth: str = "/auth"
    jwt: str = "/jwt"
    oauth2: str = "/oauth2"


class ApiPrefix(BaseModel):
    prefix: str = "/api"
    v1: ApiV1Prefix = ApiV1Prefix()


class AuthJWT(BaseModel):
    private_key_path: Path = CERTS_DIR / "jwt-private.pem"
    public_key_path: Path = CERTS_DIR / "jwt-public.pem"
    algorithm: str = "RS256"
    access_token_expires_in: int = 15  # minutes
    refresh_token_expires_days: int = 30


class DataBaseConfig(BaseModel):
    url: PostgresDsn
    echo: bool = False
    echo_pool: bool = False
    pool_pre_ping: bool = True
    max_overflow: int = 10
    pool_size: int = 50

    naming_conventions: dict[str, str] = {
        "ix": "ix_%(column_0_label)s",
        "uq": "uq_%(table_name)s_%(column_0_name)s",
        "ck": "ck_%(table_name)s_%(constraint_name)s",
        "pk": "pk_%(table_name)s",
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    }


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(".env-template", ".env"),
        case_sensitive=False,
        env_nested_delimiter="__",
        env_prefix="AUTH_SERVICE__"
    )
    debug: bool = False
    google_client_id: str
    google_client_secret: str
    oauth_redirect_uri: str
    secret_key: str
    user_service_url: str

    run: RunModel = RunModel()
    api: ApiPrefix = ApiPrefix()
    db: DataBaseConfig
    auth_jwt: AuthJWT = AuthJWT()


pydantic_settings = Settings()

