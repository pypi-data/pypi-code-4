# -*- coding: utf-8 -*-

import urllib, urllib2

from django import forms
from django.conf import settings
from django.utils.translation import ugettext_lazy as _

from .settings import SMSCOIN_VALIDATOR_PATH

class SMSKeyField(forms.CharField):
    """Field for entering SMS-code and test by validator in SMSCOIN_VALIDATOR_PATH"""
    default_error_messages = {
        'required': _('Please enter the received code.'),
        'invalid': _('An incorrect code was entered.'),
        'unknown-error': _("Unknown error. Code: %(code)s"),
    }

    def clean(self, value):
        
        value = super(SMSKeyField, self).clean(value)
        if value:
            params = {
                's_key'      : settings.SMSCOIN_KEY,
                's_pair'     : value.encode('utf-8'),
            }
            request = urllib2.Request("%s?%s" % (SMSCOIN_VALIDATOR_PATH, urllib.urlencode(params)),
                                     headers = {'User-agent': 'smscoin_key_1.0.6'})
            try:
                response = urllib2.urlopen(request).read()
            except urllib2.HTTPError, e:
                raise forms.ValidationError(self.error_messages['unknown-error'] % {'code': e.code})
            
            if not response.startswith('true'):
                raise forms.ValidationError(self.error_messages['invalid'])
        
        return value
