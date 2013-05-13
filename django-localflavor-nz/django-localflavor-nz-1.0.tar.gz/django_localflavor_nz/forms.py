# -*- coding: utf-8 -*-
"""
New Zealand specific form helpers

"""

from __future__ import absolute_import

import re

from django.core.validators import EMPTY_VALUES
from django.forms import ValidationError

from django.utils.encoding import smart_unicode
from django.utils.translation import ugettext_lazy as _

from django.forms.fields import (
        Field,
        Select, 
        RegexField
    )

from .nz_councils import NORTH_ISLAND_CHOICES
from .nz_councils import SOUTH_ISLAND_CHOICES
from .nz_regions import REGION_CHOICES
from .nz_provinces import PROVINCE_CHOICES


PHONE_08_RE = re.compile(r'^((0800\d{6})|(0800\w{6,10}))$')
PHONE_IN_RE = re.compile(r'^((0064|064|\+64|\+\+64)((\d{8})|(2\d{7,9})))$')
PHONE_NZ_RE = re.compile(r'^((0\d{8})|(02\d{7,9}))$')


class NZRegionSelect(Select):
    """
    A select widget with list of New Zealand regions as its choices.

    """
    def __init__(self, attrs=None):
        super(NZRegionSelect, self).__init__(attrs, choices=REGION_CHOICES)


class NZProvinceSelect(Select):
    """
    A select widget with list of New Zealand provinces as its choices.

    """
    def __init__(self, attrs=None):
        super(NZProvinceSelect, self).__init__(attrs, choices=PROVINCE_CHOICES)


class NZNorthIslandSelect(Select):
    """
    A select widget with list of New Zealand North Island city and district councils as its choices.

	    """
    def __init__(self, attrs=None):
        super(NZNorthIslandSelect, self).__init__(attrs, choices=NORTH_ISLAND_CHOICES)


class NZSouthIslandSelect(Select):
    """
    A select widget with list of New Zealand South Island city and district councils as its choices.

	    """
    def __init__(self, attrs=None):
        super(NZSouthIslandSelect, self).__init__(attrs, choices=NORTH_ISLAND_CHOICES)


class NZPostCodeField(RegexField):
    """
    A form field that validates its input as New Zealand postal code.
    Valid form is XXXX, where X represents digit.

    """
    default_error_messages = {
        'invalid': _('Enter valid 4 digit post code.'),
    }

    def __init__(self, *args, **kwargs):
        super(NZPostCodeField, self).__init__(r'^\d{4}$',
            *args, **kwargs)


class NZPhoneNumberField(Field):
    """
    New Zealand phone number field.

    Valid phone numbers are:

    ++64 2X XXX XXXX
    0064 2X XXX XXXX

    ++64 X XXX XXXX
    0064 X XXX XXXX

    0800 XXX XXX

    02X XXX XXXX

    0X XXX XXXX

    """
    default_error_messages = {
        'invalid': u'New Zealand land line numbers are 9 digits (including area), or mobile numbers (02, then 7-9 digits). '
        'Using internation identifier +64 and 8 digits, or 2 then 7-9 digits for mobiles is also valid format. '
        'Lastly, 0800 numbers are also valid.',
    }

    def clean(self, value):
        """
        Validate a phone number. Strips parentheses, whitespace, underscore and hyphens.

        """
        super(NZPhoneNumberField, self).clean(value)
        if value in EMPTY_VALUES:
            return u''
        value = re.sub('(\(|\)|\s+|_|-)', '', smart_unicode(value))
        value = re.sub('^(\+\+)', '00', smart_unicode(value))
        value = re.sub('^(\+)', '00', smart_unicode(value))
        phone_08_match = PHONE_08_RE.search(value)
        if phone_08_match:
            return u'%s' % phone_08_match.group(0)
        phone_nz_match = PHONE_NZ_RE.search(value)
        if phone_nz_match:
            return u'%s' % phone_nz_match.group(0)
        phone_in_match = PHONE_IN_RE.search(value)
        if phone_in_match:
            return u'%s' % phone_in_match.group(0)
        raise ValidationError(self.error_messages['invalid'])
