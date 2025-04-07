from django.contrib import admin
from .models import User


@admin.register(User)
class UserUserAdmin(admin.ModelAdmin):
    list_display = ('user_id', 'username', 'email', 'is_active', 'created_at', 'updated_at')
    search_fields = ('username', 'email')
    list_filter = ('is_active', 'created_at')
    ordering = ('-created_at',)
