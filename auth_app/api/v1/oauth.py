import requests
from django.urls import reverse
from django.shortcuts import redirect
from rest_framework.views import APIView
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema
from rest_framework.permissions import AllowAny
from authlib.integrations.django_client import OAuth

from auth_app.config import pydantic_settings

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
        Google редиректит сюда с кодом, мы обмениваем его на токен,
        а потом запрашиваем данные пользователя
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
        # здесь вы создаёте/обновляете своего юзера в БД, выдаёте JWT и т.п.
        return Response({
            'token': token,
            'user': user_info,
        })


