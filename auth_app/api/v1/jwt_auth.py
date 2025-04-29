# auth_app/api/v1/jwt_views.py
from http.client import HTTPException

import httpx
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth import get_user_model
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import AuthenticationFailed, PermissionDenied
from rest_framework.permissions import AllowAny

from auth_app.services.security import (
    validate_password,
    decode_jwt,
    encode_jwt,
)
from auth_app.api.core.helpers import (
    create_access_token,
    create_refresh_token,
)
from auth_app.crud import user_crud
from auth_app.models import AuthUser
from auth_app.api.v1.serializers import TokenSerializer, RefreshSerializer, AuthUserSerializer


class LoginApiView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")
        if not username or not password:
            raise AuthenticationFailed("Username and password is required")

        try:
            response = user_crud.get_user_service_user_by_username(username)
        except httpx.HTTPError:
            return Response(
                {"detail": "Failed to get user profile in user_service"},
                status=status.HTTP_502_BAD_GATEWAY,
            )
        except Exception:
            return Response(
                {"detail": "Internal Server Error"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        user_id = response.get("user_id")
        email = response.get("email")
        is_active = response.get("is_active")
        if not is_active:
            raise PermissionDenied("User is inactive")

        try:
            auth_user = AuthUser.objects.get(user_id=user_id)
        except ObjectDoesNotExist:
            raise AuthenticationFailed("Invalid username or password")

        if not validate_password(password, auth_user.password):
            raise AuthenticationFailed("Invalid username or password")

        access = create_access_token(user_id, email)
        refresh = create_refresh_token(user_id, email)

        data = {"access_token": access, "refresh_token": refresh, "token_type": "Bearer"}
        serializer = TokenSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class RefreshApiView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        token = request.data.get("refresh_token")
        if not token:
            raise AuthenticationFailed("Invalid refresh token")

        try:
            payload = decode_jwt(token)
        except Exception as e:
            raise AuthenticationFailed(str(e))

        user_id = payload.get("user_id")
        email = payload.get("email")
        if not user_id:
            raise AuthenticationFailed("Invalid token payload")

        new_access = create_access_token(user_id=user_id, email=email)
        data = {"access_token": new_access, "refresh_token": None, "token_type": "Bearer"}
        serializer = TokenSerializer(data=data, context={"partial": True})
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data, status=status.HTTP_200_OK)