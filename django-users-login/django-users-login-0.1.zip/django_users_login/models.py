#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import (absolute_import, division, print_function)

from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import ugettext as _


class Perfil(User):
    pass


class LoginAttempt(models.Model):
    ip = models.IPAddressField(verbose_name=_('ip address'))
    credentials = models.CharField(max_length=255, verbose_name=_('credentials'))
    criado_em = models.DateTimeField(auto_now_add=True)
    alterado_em = models.DateTimeField(auto_now=True)
    ativo = models.BooleanField(default=True)

    @classmethod
    def on_fail_to_login(self):
        register_fail = LoginAttempt()



