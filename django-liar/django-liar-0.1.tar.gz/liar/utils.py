# -*- coding: utf-8 -*-
from types import ModuleType
from django.core.urlresolvers import RegexURLResolver
from django.conf import settings
from django.conf.urls import url as default_url


INVALID_APPS = getattr(settings, 'INVALID_APPS', [])


class CustomRegexURLResolver(RegexURLResolver):
    def resolve(self, path):
        if type(self.urlconf_module) == ModuleType:
            module = self.urlconf_module.__package__
        else:
            module = self.app_name
        if module not in INVALID_APPS:
            return super(CustomRegexURLResolver, self).resolve(path)


def url(regex, view, kwargs=None, name=None, prefix=''):
    if isinstance(view, (list, tuple)):
        urlconf_module, app_name, namespace = view
        return CustomRegexURLResolver(regex, urlconf_module, kwargs, app_name=app_name, namespace=namespace)
    return default_url(regex, view, kwargs, name, prefix)


__author__ = 'lalo'
