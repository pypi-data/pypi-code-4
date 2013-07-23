# coding: utf8

from django.conf import settings
from django.core.urlresolvers import resolve

from .site import get_default_site_url


def company_name(request):
    return {'company_name': getattr(settings, 'COMPANY_NAME')}


def site_url(request):
    return {'site_url': get_default_site_url()}


def url_name(request):
    try:
        return {'url_name': resolve(request.path_info).url_name}
    except:
        return {'url_name': None}


def url_namespace(request):
    try:
        return {'url_namespace': resolve(request.path_info).namespace}
    except:
        return {'url_namespace': None}


def url_namespaces(request):
    try:
        return {'url_namespaces': resolve(request.path_info).namespaces}
    except:
        return {'url_namespaces': None}
