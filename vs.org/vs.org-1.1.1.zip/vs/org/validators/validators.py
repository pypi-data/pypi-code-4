################################################################
# vs.org (C) 2011, Veit Schiele
################################################################

# $Id$

import re

from zope.interface import implements
from Products.validation.interfaces.IValidator import IValidator
from Products.validation.validators.RegexValidator import RegexValidator

class VSAddressValidator(object):

    implements(IValidator)

    def __init__(self, name, title='', description=''):
        self.name = name
        self.title = title or name
        self.description = description
        self.re_poBox = re.compile('^\d+$')
        self.re_zipCode = re.compile('^\d+$')
        self.re_geoCode = re.compile('^\s*\d+\.\d+\s*,\s*\d+\.\d+\s*$')

    def __call__(self, value, *args, **kwargs):
        error_msg = ""
        for val in value[:-1]:
            if val['poBox']:
                if val['street']:
                    error_msg = "Dont use street and postalBox together"

                if not self.re_poBox.match(val['poBox']):
                    error_msg = "Doesnt seem to be a valid postal-box number"

            if val['zipCode'] and (not self.re_zipCode.match(val['zipCode'])):
                error_msg = "Doesnt seem to be a valid zip-code"

            if val['geocode'] and (not self.re_geoCode.match(val['geocode'])):
                error_msg = "Doesnt seem to be a valid geo-code"

            if not val['city']:
                error_msg = "Missing value for city"

        if error_msg:
            return error_msg
        else:
            return True

isVsAddress = VSAddressValidator(
        'isVSAddress', title="Address Validator",
        description="Validator for Addresses"
    )

