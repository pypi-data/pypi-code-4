##############################################################################
#
# Copyright (c) 2007 Zope Foundation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Currency Field implementation
"""
import decimal
import zope.interface
import zope.schema
from zope.schema.fieldproperty import FieldProperty

from z3c.currency import interfaces

class Currency(zope.schema.Orderable, zope.schema.Field):
    zope.interface.implements(interfaces.ICurrency)

    precision = FieldProperty(interfaces.ICurrency['precision'])
    unit = FieldProperty(interfaces.ICurrency['unit'])

    def __init__(self, precision=interfaces.CENTS, unit=u'$', *args, **kw):
        super(Currency, self).__init__(*args, **kw)
        self.precision = precision
        self.unit = unit

    def _validate(self, value):
        if not isinstance(value, decimal.Decimal):
            raise interfaces.WrongCurrencyType(type(value).__name__)

        exp = value.as_tuple().exponent
        if self.precision is interfaces.DOLLARS and exp != 0:
            raise interfaces.IncorrectValuePrecision(self.precision)

        if self.precision is interfaces.CENTS and exp != -2:
            raise interfaces.IncorrectValuePrecision(self.precision)

        super(Currency, self)._validate(value)
