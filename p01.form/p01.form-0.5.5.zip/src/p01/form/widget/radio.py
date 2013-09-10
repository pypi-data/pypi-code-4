###############################################################################
#
# Copyright (c) 2012 Projekt01 GmbH.
# All Rights Reserved.
#
###############################################################################
"""Checkbox widget with div tag separation
$Id: radio.py 3798 2013-07-18 03:30:48Z roger.ineichen $
"""
__docformat__ = 'restructuredtext'

import zope.component
import zope.interface
import zope.schema.interfaces

import z3c.form.interfaces
import z3c.form.widget
import z3c.form.browser.radio

from p01.form import interfaces
from p01.form.layer import IFormLayer
from p01.form.widget.widget import setUpWidget


class RadioWidget(z3c.form.browser.radio.RadioWidget):
    """Input type radio widget implementation using div instead of span tag.
    """

    zope.interface.implementsOnly(interfaces.IRadioWidget)

    hint = None

    klass = u'radio'
    css = u'radio'

    @property
    def css(self):
        """Returns a CSS layout wrapper class name"""
        if self.hint is not None:
            # use hint as css class if hint is given
            return u'hint'
        else:
            # use text as css class
            return 'radio'


class DivRadioWidget(RadioWidget):
    """RadioWidget using a div wrapper for option tags"""


# get
@zope.component.adapter(zope.schema.interfaces.IField, IFormLayer)
@zope.interface.implementer(z3c.form.interfaces.IFieldWidget)
def getRadioWidget(field, request):
    """IFieldWidget factory for RadioWidget."""
    return z3c.form.widget.FieldWidget(field, RadioWidget(request))


@zope.component.adapter(zope.schema.interfaces.IField, IFormLayer)
@zope.interface.implementer(z3c.form.interfaces.IFieldWidget)
def getDivRadioWidget(field, request):
    """IFieldWidget factory for RadioWidget."""
    return z3c.form.widget.FieldWidget(field, DivRadioWidget(request))


# setup
def setUpRadioWidget(**kw):
    """Widget creator method supporting kw arguments"""
    return setUpWidget(RadioWidget, **kw)


def setUpDivRadioWidget(**kw):
    """Widget creator method supporting kw arguments"""
    return setUpWidget(DivRadioWidget, **kw)
