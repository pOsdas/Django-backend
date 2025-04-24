from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import exceptions, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from drf_spectacular.utils import extend_schema

from auth_app.crud.tokens_crud import get_username_by_static_auth_token
from auth_app.config import pydantic_settings
from auth_app.crud.session_crud import create_session, get_session


@extend_schema(tags=["Cookies"])
class CookieSessionAPIView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    def get(self, request):
        """
        Получить куку
        """
        session_id = request.COOKIES.get(pydantic_settings.cookie_session_id_key)
        if not session_id:
            raise exceptions.AuthenticationFailed("Session not found")

        data = get_session(session_id)
        if data is None:
            raise exceptions.AuthenticationFailed("Session expired or invalid")

        return Response(data)


# @router.get("/logout-cookie/")
# def demo_auth_cookie_logout(
#         response: Response,
#         session_id: str = Cookie(alias=COOKIE_SESSION_ID_KEY),
#         user_session_data: dict = Depends(get_session_data)
# ):
#     COOKIES.pop(session_id)
#     response.delete_cookie(COOKIE_SESSION_ID_KEY)
#     username = user_session_data["username"]
#     return {
#         "message": f"Bye, {username}",
#     }
