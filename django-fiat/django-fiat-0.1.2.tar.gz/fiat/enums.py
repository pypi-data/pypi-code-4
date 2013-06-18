# -*- coding: utf-8 -*-

from django.utils.translation import gettext as _

from enumerify.enum import Enum

class SymbolPosition(Enum):
    SUFFIX = 0
    PREFIX = 1

    i18n = (
        _('Suffix'),
        _('Prefix')
    )


class CurrencyMode(Enum):
    CODE = 0
    SIGN = 1
    SYMBOL = 2

    i18n = (
        _('Code'),
        _('Sign'),
        _('Symbol')
    )


class CountryTaxMode(Enum):
    INCLUSIVE = 0
    EXCLUSIVE = 1

    i18n = (
        _('Inclusive'),
        _('Exclusive'),
    )