# coding: utf8

from django.contrib import admin
from django.conf import settings


def send_activation_key(modeladmin, request, queryset):
    """ Sends the user an activation key. """

    map(lambda u: u.send_activation_key(), queryset)
send_activation_key.short_description = 'Send activation key.'

if getattr(settings, 'AUTH_USER_MODEL') == 'authentication.User':

    from .models import User

    class UserAdmin(admin.ModelAdmin):
        actions = (send_activation_key,)
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
