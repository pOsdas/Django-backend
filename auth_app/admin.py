from django.contrib import admin
from .models import AuthUser


@admin.register(AuthUser)
class AuthUserAdmin(admin.ModelAdmin):
    list_display = ('user_id', 'updated_at', 'refresh_token')
    search_fields = ('user_id',)
