import httpx
import requests
from django.urls import reverse
from rest_framework import status
from django.shortcuts import redirect
from rest_framework.views import APIView
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema
from rest_framework.permissions import AllowAny
from authlib.integrations.django_client import OAuth

from auth_app.models import AuthUser
from auth_app.crud import user_crud
from auth_app.config import pydantic_settings
from auth_app.api.core.helpers import create_access_token, create_refresh_token

oauth = OAuth()

oauth.register(
    name='google',
    client_id=pydantic_settings.google_client_id,
    client_secret=pydantic_settings.google_client_secret,
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={
        'scope': 'openid email profile',
    }
)


@extend_schema(tags=["Google"])
class GoogleLoginView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        """
        Перенаправляем юзера на Google для авторизации
        """
        redirect_uri = request.build_absolute_uri(
            reverse('google-callback')
        )
        return oauth.google.authorize_redirect(request, redirect_uri)


@extend_schema(tags=["Google"])
class GoogleCallbackView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        """
        Google редиректит сюда
        """
        # получаем токен
        token = oauth.google.authorize_access_token(request)
        # достаём userinfo
        resp = requests.get(
            'https://www.googleapis.com/oauth2/v1/userinfo',
            headers={'Authorization': f"Bearer {token['access_token']}"}
        )
        resp.raise_for_status()
        user_info = resp.json()

        username = user_info.get('name')
        email = user_info.get('email')

        # Запрос на создание в user_service
        try:
            response = user_crud.create_user_service_user(username, email)
            user_id = response.get("user_id")
            if not user_id:
                raise ValueError("Missing user ID in response")

        except (httpx.HTTPError, ValueError) as exc:
            print(f"User service error: {str(exc)}")
            return Response(
                {"detail": "Failed to create user profile in user_service"},
                status=status.HTTP_502_BAD_GATEWAY,
            )

        # Создаем пользователя тут
        new_access = create_access_token(user_id=user_id, email=email)
        new_refresh = create_refresh_token(user_id=user_id, email=email)

        AuthUser.objects.update_or_create(
            user_id=user_id,
            defaults={'refresh_token': new_refresh},
        )

        return Response({
            'access_token': new_access,
            'user': user_info,
        })


