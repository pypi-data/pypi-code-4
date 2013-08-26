# -*- coding: utf8 -*-
from django.conf import  settings

__author__ = 'ir4y'

USER = settings.MOBILVEST_USER
PASSWORD = settings.MOBILVEST_PASSWORD
SENDER = settings.MOBILVEST_SENDER

SEND_GATE = getattr(settings,'MOBILVEST_SEND_GATE','http://cab.mobilvest.ru/xml/')
STATUS_GATE = getattr(settings,'MOBILVEST_STATUS_GATE','http://cab.mobilvest.ru/xml/state.php')