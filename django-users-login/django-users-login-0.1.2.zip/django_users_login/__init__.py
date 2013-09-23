#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import (absolute_import, division, print_function)
from django.conf import settings

__author__ = 'Geraldo Andrade (geraldo@geraldoandrade.com)'

# settings django settings
settings.LOGIN_URL = '/users/login'

settings.LOGIN_REDIRECT_URL = '/'

settings.LOGOUT_URL = '/users/logout'

settings.LOGOUT_URL_REDIRECT = '/'