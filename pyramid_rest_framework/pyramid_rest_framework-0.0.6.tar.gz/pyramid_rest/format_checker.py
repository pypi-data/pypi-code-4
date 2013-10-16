#-*- coding: utf-8 -*-
from jsonschema._format import FormatChecker, _checks_drafts
import re

@_checks_drafts("url")
def is_url(instance):
    u"""
        Испозует валидацию из Django:
        
            https://github.com/django/django/blob/master/django/core/validators.py#L47
            
    """
    regex = re.compile(
        r'^(?:http|ftp)s?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'  # domain...
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}|'  # ...or ipv4
        r'\[?[A-F0-9]*:[A-F0-9:]+\]?)'  # ...or ipv6
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    return instance and regex.match(instance)

@_checks_drafts("host")
def is_host(instance):
    regex = re.compile("((?:http|https)://[^/]+)")
    return instance and regex.match(instance)

class OwnFormatChecker(FormatChecker):
    """
        Класс для проверки валидации в json schema след. типов:
        
            * email
            * uri
            * hostname
            * url (simple version of uri, see :func:`pyramid_rest.format_checker.is_url`
            * host (simple pattern for validationg hosts: ((?:http|https)://[^/]+) )
            
    """