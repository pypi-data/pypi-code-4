# -*- coding: utf-8 -*-
"""
Define your custom middlewares in this file.
"""
from django.conf import settings
from django.contrib.auth.backends import RemoteUserBackend
from django.contrib.auth.middleware import RemoteUserMiddleware
from django.contrib.auth.models import Group

__author__ = "flanker"


class ProxyRemoteUserMiddleware(RemoteUserMiddleware):
    header = "HTTP_PROXY_REMOTE_USER"


GROUPS = {}


class DefaultGroupRemoteUserBackend(RemoteUserBackend):

    def configure_user(self, user):
        """
        Configures a user after creation and returns the updated user.

        By default, returns the user unmodified.
        """
        print(user)
        if GROUPS.get(settings.DEFAULT_GROUP) is None:
            GROUPS[settings.DEFAULT_GROUP] = Group.objects.get_or_create(name=str(settings.DEFAULT_GROUP))[0]
        user.groups.add(GROUPS[settings.DEFAULT_GROUP])
        user.save()
        return user
