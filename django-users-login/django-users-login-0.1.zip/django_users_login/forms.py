#!/usr/bin/python
# -*- coding: utf-8 -*-

__author__ = 'Geraldo Andrade'

from django.forms import Form, CharField, PasswordInput
from django.core import validators


class FormLogin(Form):
    username = CharField(min_length=4, max_length=100)
    password = PasswordInput()


class FormPasswordRecover(Form):
    email = CharField(max_length=255, validators=[validators.validate_email], required=True)


