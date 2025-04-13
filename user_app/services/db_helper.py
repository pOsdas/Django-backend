import psycopg2
from urllib.parse import urlparse

from user_app.config import pydantic_settings as settings


def create_db_if_not_exists():
    parsed = urlparse(str(settings.db.url))
    target_db = parsed.path.lstrip("/")
    user = parsed.username
    password = parsed.password
    host = parsed.hostname
    port = parsed.port

    conn = psycopg2.connect(dbname="postgres", user=user, password=password, host=host, port=port)
    conn.autocommit = True
    cur = conn.cursor()

    cur.execute("SELECT 1 FROM pg_database WHERE datname = %s", (target_db,))
    exists = cur.fetchone()

    if not exists:
        print(f"База данных '{target_db}' не найдена. Создаю...")
        cur.execute(f"CREATE DATABASE {target_db}")
    else:
        print(f"База данных '{target_db}' уже существует")

    cur.close()
    conn.close()


create_db_if_not_exists()