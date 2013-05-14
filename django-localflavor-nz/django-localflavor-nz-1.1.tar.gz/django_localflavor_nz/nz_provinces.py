# -*- coding: utf-8 -*-
""" New Zealand Provinces.

See "The Anniversary Day of the Province" at the source URL.

Source: http://www.dol.govt.nz/er/holidaysandleave/publicholidays/publicholidaydates/future-dates.asp

"""

from __future__ import absolute_import

from django.utils.translation import ugettext_lazy as _


PROVINCE_CHOICES = (
    ('Auckland', _('Auckland')),
    ('Taranaki', _('Taranaki')),
    ('Hawkes Bay', _('Hawkes\' Bay')),
    ('Wellington', _('Wellington')),
    ('Marlborough', _('Marlborough')),
    ('Nelson', _('Nelson')),
    ('Canterbury', _('Canterbury')),
    ('South Canterbury', _('South Canterbury')),
    ('Westland', _('Westland')),
    ('Otago', _('Otago')),
    ('Southland', _('Southland')),
    ('Chatham Islands', _('Chatham Islands')),
)
