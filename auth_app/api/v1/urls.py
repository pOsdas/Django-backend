from django.urls import path
from .basic_auth import (
    BasicAuthCredentialsAPIView,
    RegisterUserAPIView,
    GetUsersAPIView,
    BasicAuthUsernameAPIView,
    CheckTokenAuthAPIView,
    DeleteAuthUserAPIView,
)
from .cookies import (
    CookieSessionAPIView,
)

urlpatterns = [
    path('basic-auth/', BasicAuthCredentialsAPIView.as_view(), name='basic-auth'),
    path('register/', RegisterUserAPIView.as_view(), name='register'),
    path('get_users/', GetUsersAPIView.as_view(), name='get-users'),
    path('basic-auth-username/', BasicAuthUsernameAPIView.as_view(), name='basic-auth-username'),
    path('check-token-auth/', CheckTokenAuthAPIView.as_view(), name='check-token-auth'),
    path('<int:user_id>/', DeleteAuthUserAPIView.as_view(), name='delete-auth-user'),
    path('cookie-session/', CookieSessionAPIView.as_view(), name='cookie-session'),
]
