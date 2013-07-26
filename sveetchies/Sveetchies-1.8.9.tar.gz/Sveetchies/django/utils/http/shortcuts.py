# -*- coding: utf-8 -*-
from django.template import loader
from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.http import HttpResponseForbidden
from django.shortcuts import _get_queryset

def render_to_403(*args, **kwargs):
    """
    Returns a HttpResponseForbidden whose content is filled with the result of calling
    django.template.loader.render_to_string() with the passed arguments.
    """
    if not isinstance(args,list):
        args = []
        args.append('403.html')              

    httpresponse_kwargs = {'mimetype': kwargs.pop('mimetype', None)}
    response = HttpResponseForbidden(loader.render_to_string(*args, **kwargs), **httpresponse_kwargs)              

    return response  

def get_object_or_403(klass, *args, **kwargs):
    """
    Uses get() to return an object, or raises a Http403 exception if the object
    does not exist.

    klass may be a Model, Manager, or QuerySet object. All other passed
    arguments and keyword arguments are used in the get() query.

    Note: Like with get(), an MultipleObjectsReturned will be raised if more than one
    object is found.
    """
    queryset = _get_queryset(klass)
    try:
        return queryset.get(*args, **kwargs)
    except queryset.model.DoesNotExist:
        raise Http404('You are not allowed to access to this ressource.')
