# -*- coding: utf-8 -*-
"""
Define your custom context processors in this file.
"""
from updoc.models import LastDocs

__author__ = "flanker"


def context_user(request):
    """Add the current user to the context.
    User is taken from the current :class:`django.core.http.HttpRequest`
    and binded to `user`."""
    return {'user': request.user, }


def most_checked(request):
    user = request.user if request.user.is_authenticated() else None
    most_checked_ = LastDocs.objects.filter(user=user).select_related().order_by('-count')[0:6]
    return {'updoc_most_checked': most_checked_}