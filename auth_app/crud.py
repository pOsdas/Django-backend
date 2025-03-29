"""
create
read
update
delete
"""
from typing import Sequence, Optional

from asgiref.sync import sync_to_async

from auth_app.models import AuthUser
from auth_app.security import hash_password

# ### fake users db
john = AuthUser(
    user_id=1,
    password=hash_password("qwerty"),
    # updated_at
    refresh_token="dummy_refresh_token"
)

sam = AuthUser(
    user_id=2,
    password=hash_password("secret"),
    # updated_at
    refresh_token="second_dummy_refresh_token"
)


test = AuthUser(
    user_id=3,
    password=hash_password("test"),
    # updated_at
    refresh_token="second_dummy_refresh_token"
)

users_db: dict[int, AuthUser] = {
    john.user_id: john,
    sam.user_id: sam,
}
user_id_to_password = {"3": "test"}
static_auth_token_to_user_id = {
    "90609ed991fcca984411d4b6e1ba7": john.user_id,
}
# ### never do like that


async def get_all_users() -> Sequence[AuthUser]:
    users = await AuthUser.objects.order_by("user_id")
    return users


async def get_auth_user(
        user_id: int,
) -> Optional[AuthUser]:
    try:
        user = await sync_to_async(AuthUser.objects.get)(user_id=user_id)
        return user
    except AuthUser.DoesNotExist:
        return None


async def delete_auth_user(
        user_id: int,
) -> None:
    user = await get_auth_user(user_id)
    if user:
        await sync_to_async(user.delete)()

