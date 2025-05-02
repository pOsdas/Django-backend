from django.db import models


class AuthUser(models.Model):
    user_id = models.AutoField(primary_key=True)
    password = models.BinaryField()
    refresh_token = models.TextField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_login = models.DateTimeField(auto_now=True)

    objects = models.Manager()

    def __str__(self) -> str:
        return f"{self.__class__.__name__}(id={self.user_id})"

    def __repr__(self) -> str:
        return str(self)
