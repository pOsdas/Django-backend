# from pprint import pprint
from dotenv import load_dotenv
from pydantic import BaseModel, PostgresDsn
from pydantic_settings import BaseSettings, SettingsConfigDict

# Принудительно загружаем .env и .env-template
load_dotenv(encoding="utf-8")


class RunModel(BaseModel):
    host: str = "127.0.0.1"
    port: int = 8006


class ApiV1Prefix(BaseModel):
    prefix: str = "/v1"
    users: str = "/users"


class ApiPrefix(BaseModel):
    prefix: str = "api"
    v1: ApiV1Prefix = ApiV1Prefix()


class DataBaseConfig(BaseModel):
    url: PostgresDsn
    echo: bool = False
    echo_pool: bool = False
    max_overflow: int = 10
    pool_pre_ping: bool = True
    pool_recycle: int = 600
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
        env_file=("user_app/.env-template", "user_app/.env"),
        case_sensitive=False,
        env_nested_delimiter="__",
        env_prefix="USER_SERVICE__"
    )
    debug: bool = False
    google_client_id: str
    google_client_secret: str
    oauth_redirect_uri: str
    secret_key: str
    auth_service_url: str

    run: RunModel = RunModel()
    api: ApiPrefix = ApiPrefix()
    db: DataBaseConfig


pydantic_settings = Settings()
# pprint(pydantic_settings.model_dump())
