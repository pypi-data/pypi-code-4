# coding: utf8

from django.conf import settings
from django.core.urlresolvers import resolve
from django.http import Http404

from .site import get_default_site_url


def company_name(request):
    return {'company_name': getattr(settings, 'COMPANY_NAME')}


def site_url(request):
    return {'site_url': get_default_site_url()}


def url_name(request):
    try:
        return {'url_name': resolve(request.path_info).url_name}
    except Http404:
        return {'url_name': None}


def url_namespace(request):
    try:
        return {'url_namespace': resolve(request.path_info).namespace}
    except Http404:
        return {'url_namespace': None}


def url_namespaces(request):
    try:
        return {'url_namespaces': resolve(request.path_info).namespaces}
    except Http404:
        return {'url_namespaces': None}


def url_qualifier(request):
    try:
        match = resolve(request.path_info)
        return {'url_qualifier': '%s:%s' % (
            match.url_namespace, match.url_name)}
    except Http404:
        return {'url_qualifier': None}
