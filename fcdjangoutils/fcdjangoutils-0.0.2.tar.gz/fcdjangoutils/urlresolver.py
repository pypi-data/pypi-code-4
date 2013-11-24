# -*- coding: utf-8 -*-
import django.core.urlresolvers
import urlparse

def urlparams(request):
    view, args, kwargs = django.core.urlresolvers.resolve(request.path)
    # Django 1.3 code...
    # res = {}
    # for name in ('func', 'args', 'kwargs', 'url_name', 'app_name', 'namespace', 'namespaces'):
    #     res[name] = getattr(data, name)
    return {'urlparams': {'func': view, 'args': args, 'kwargs': kwargs}}
