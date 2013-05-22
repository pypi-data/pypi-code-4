# coding: utf8

from django.contrib import admin
from django.conf import settings

if getattr(settings, 'AUTH_USER_MODEL') == 'authentication.User':

    from .models import User

    class UserAdmin(admin.ModelAdmin):
        list_display = (
            'email',
            'display_name',
            'is_active',
            'is_staff',
            'is_superuser',
            'created',
            'modified',
        )

    admin.site.register(User, UserAdmin)
