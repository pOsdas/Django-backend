from django.urls import path
from .users import (
    CreateUserAPIView,
    GetUserAPIView,
    GetUserByUsernameAPIView,
    GetUsersAPIView,
    UpdateUserAPIView,
    DeleteUserAPIView,
)

urlpatterns = [
    path('create_user/', CreateUserAPIView.as_view(), name='create-user'),
    path('get_users/', GetUsersAPIView.as_view(), name='get-users'),
    path('<int:user_id>/', GetUserAPIView.as_view(), name='get-user'),
    path('username/<str:username>/', GetUserByUsernameAPIView.as_view(), name='get_user_by_username'),
    path('change_user/<int:user_id>/', UpdateUserAPIView.as_view(), name='update_user'),
    path('<int:user_id>/', DeleteUserAPIView.as_view(), name='delete_user_service_user'),
]
