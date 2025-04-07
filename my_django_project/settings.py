# my_django_project/settings.py

import os
from pathlib import Path
import dj_database_url

# Импортируем pydantic-настройки из auth_app/config.py
from auth_app.config import pydantic_settings

# Корневая директория проекта
BASE_DIR = Path(__file__).resolve().parent

# Основные настройки
SECRET_KEY = pydantic_settings.secret_key
DEBUG = pydantic_settings.debug
ALLOWED_HOSTS = []

# Настройка базы данных
DATABASES = {
    'default': dj_database_url.parse(str(pydantic_settings.db.url))
}
# DATABASES["default"]["ENGINE"] = "django.db.backends.postgresql_async"
DATABASES["default"]["ENGINE"] = "django.db.backends.postgresql"

# Установленные приложения
INSTALLED_APPS = [
    # Стандартные приложения Django
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'rest_framework_simplejwt',
    # Ваши приложения
    'auth_app',
    'user_app',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# Основной роутер URL (можно указать my_django_project.urls, если у вас такой файл)
ROOT_URLCONF = 'my_django_project.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

ASGI_APPLICATION = 'my_django_project.asgi.application'
# WSGI_APPLICATION = 'my_django_project.wsgi.application'

# Статические файлы
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'static'

# (Опционально) Настройки Django REST Framework
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework.authentication.BasicAuthentication',
    ),
}
