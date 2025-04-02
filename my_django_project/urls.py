from django.contrib import admin
from django.urls import path, include
from auth_app.config import pydantic_settings

API_PREFIX = pydantic_settings.api.prefix
API_V1_PREFIX = pydantic_settings.api.v1.prefix

urlpatterns = [
    path("admin/", admin.site.urls),
    path(f"{API_PREFIX}{API_V1_PREFIX}/auth/", include("auth_app.api.v1.urls")),
    path(f"{API_PREFIX}{API_V1_PREFIX}/users/", include("user_app.api.v1.urls")),
]
