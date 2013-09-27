##############################################################################
#
# Copyright (c) 2007-2013 Zope Foundation and Contributors.
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
"""Currency Field to Text-based widget implementation
"""
import decimal
import zope.component
import zope.interface
from z3c.form.interfaces import IDataConverter, IWidget
from z3c.currency import interfaces
from zope.i18n import format

class CurrencyConverter(object):
    """Converts currency fields to text representations."""
    zope.component.adapts(interfaces.ICurrency, IWidget)
    zope.interface.implements(IDataConverter)

    inputPatterns = (
        '#,##0;-#,##0', '#,##0.00;-#,##0.00', '#,##0.00###;-#,##0.00###')
    outputPatterns = (
        '#,##0;-#,##0', '#,##0.00;-#,##0.00', '#,##0.00###;-#,##0.00###')
    quantization = ('1', '0.01', None)


    def __init__(self, field, widget):
        self.field = field
        self.widget = widget

    def toWidgetValue(self, value):
        """See interfaces.IDataConverter"""
        if value is self.field.missing_value:
            return u''
        formatter = format.NumberFormat(
            self.outputPatterns[self.field.precision])
        return formatter.format(value)

    def toFieldValue(self, value):
        """See interfaces.IDataConverter"""
        if value == u'':
            return self.field.missing_value
        formatter = format.NumberFormat()
        formatter.type = decimal.Decimal
        for pattern in self.inputPatterns:
            try:
                res = formatter.parse(value, pattern)
            except (format.NumberParseError, ValueError):
                continue
            # Make sure that the resulting decimal has the right precision.
            if self.field.precision == interfaces.SUBCENTS:
                return res
            return res.quantize(
                decimal.Decimal(self.quantization[self.field.precision]))
        raise ValueError('Could not parse %r.' %value)

    def __repr__(self):
        return '<DataConverter from %s to %s>' %(
            self.field.__class__.__name__, self.widget.__class__.__name__)
