# -*- coding: utf-8 -*-
"""
Sveetchies-tribune

Currently an alpha prototype with :

* An awesome project title;
* Data models;
* Queryset filtering API for "standard" tribune behavior;
* All stuff for base remote views and remote views for plain-text, JSON and XML;
* ...
* Profit !

"""
from django.conf import settings

__version__ = '0.1.0'

TRIBUNE_LOCKED = getattr(settings, 'TRIBUNE_LOCKED', False)

TRIBUNE_MESSAGES_DEFAULT_LIMIT = getattr(settings, 'TRIBUNE_MESSAGES_DEFAULT_LIMIT', 50)
TRIBUNE_MESSAGES_MAX_LIMIT = getattr(settings, 'TRIBUNE_MESSAGES_MAX_LIMIT', 100)
