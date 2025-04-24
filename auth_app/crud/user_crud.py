"""
create
read
update
delete
"""
import redis
from typing import Sequence, Optional
from django.core.exceptions import ObjectDoesNotExist

from auth_app.models import AuthUser


redis_client = redis.Redis(host="localhost", port=6379, db=0, decode_responses=True)


# ---- users ----
def get_all_users() -> Sequence[AuthUser]:
    return list(AuthUser.objects.order_by("user_id"))


def get_auth_user(
        user_id: int,
) -> Optional[AuthUser]:
    try:
        user = AuthUser.objects.get(user_id=user_id)
        return user
    except ObjectDoesNotExist:
        raise


def delete_auth_user(
        user_id: int,
) -> None:
    user = get_auth_user(user_id)
    if user:
        user.delete()
