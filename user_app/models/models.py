from django.db import models


class User(models.Model):
    user_id = models.AutoField(primary_key=True)
    username = models.TextField(max_length=32, unique=True, db_index=True)
    email = models.EmailField(max_length=255, unique=True, db_index=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = models.Manager()

    def __str__(self) -> str:
        return f"{self.__class__.__name__}(user_id={self.user_id}, username={self.username!r})"

    def __repr__(self) -> str:
        return str(self)
