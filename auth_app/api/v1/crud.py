from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.permissions import AllowAny, IsAuthenticated

from auth_app.crud import user_crud
from .serializers import AuthUserSerializer


@extend_schema(tags=["CRUD"])
class GetUsersAPIView(APIView):
    # permission_classes = [IsAuthenticated]
    permission_classes = [AllowAny]
    serializer = AuthUserSerializer
    authentication_classes = []

    def get(self, request):
        try:
            users = user_crud.get_all_users()
            if not users:
                return Response(
                    {"detail": "Users not found"},
                    status=status.HTTP_404_NOT_FOUND
                )

            serializer = AuthUserSerializer(users, many=True)
            return Response(serializer.data)

        except Exception as exc:
            print(f"Error while fetching users: {str(exc)}")
            return Response(
                {"detail": "Internal server error"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


@extend_schema(tags=["CRUD"])
class GetUserAPIView(APIView):
    # permission_classes = [IsAuthenticated]
    permission_classes = [AllowAny]
    authentication_classes = []
    serializer = AuthUserSerializer

    def get(self, request, user_id):
        try:
            user = user_crud.get_auth_user(user_id=user_id)
        except ObjectDoesNotExist:
            return Response(
                {"detail": "User not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = AuthUserSerializer(user)
        return Response(serializer.data)


@extend_schema(tags=["CRUD"])
class DeleteAuthUserAPIView(APIView):
    """
    Вызывается через user_service, \n
    Через эту сторону синхронизация не происходит
    """
    def delete(self, request, user_id: int):
        try:
            user_crud.delete_auth_user(user_id)
        except ObjectDoesNotExist:
            return Response(
                {"detail": f"User with {user_id} not found in auth_service"},
                status=status.HTTP_404_NOT_FOUND
            )
        return Response({"message": "Auth user deleted"})
