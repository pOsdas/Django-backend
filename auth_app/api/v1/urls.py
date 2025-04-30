from django.urls import path
from .basic_auth import (
    BasicAuthCredentialsAPIView,
    RegisterUserAPIView,
    BasicAuthUsernameAPIView,
    CheckTokenAuthAPIView,
)
from .cookies import (
    CookieSessionAPIView,
)
from .jwt_auth import (
    LoginApiView,
    RefreshApiView,
)
from .debug import (
    debug_redis_sessions
)
from .crud import (
    GetUsersAPIView,
    GetUserAPIView,
    DeleteAuthUserAPIView,
)
from .oauth import (
    GoogleLoginView,
    GoogleCallbackView,
)

urlpatterns = [
    path('basic-auth/', BasicAuthCredentialsAPIView.as_view(), name='basic-auth'),
    path('register/', RegisterUserAPIView.as_view(), name='register'),
    path('get_users/', GetUsersAPIView.as_view(), name='get-users'),
    path('<int:user_id>/', GetUserAPIView.as_view(), name='get-user'),
    path('basic-auth-username/', BasicAuthUsernameAPIView.as_view(), name='basic-auth-username'),
    path('check-token-auth/', CheckTokenAuthAPIView.as_view(), name='check-token-auth'),
    path('<int:user_id>/', DeleteAuthUserAPIView.as_view(), name='delete-auth-user'),
    path('cookie-session/', CookieSessionAPIView.as_view(), name='cookie-session'),
    path('jwt/login/', LoginApiView.as_view(), name="jwt-login"),
    path('jwt/refresh/', RefreshApiView.as_view(), name="jwt-refresh"),
    path('redis-sessions/', debug_redis_sessions),
    path('login/google/', GoogleLoginView.as_view(), name="google-login"),
    path('callback/google/', GoogleCallbackView.as_view(), name="google-callback"),
]
