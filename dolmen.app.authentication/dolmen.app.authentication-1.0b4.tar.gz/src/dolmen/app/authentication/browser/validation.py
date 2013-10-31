# -*- coding: utf-8 -*-

from zope.schema import ValidationError
from zope.interface import implements
from zope.formlib.interfaces import IWidgetInputError


class UserRegistrationError(ValidationError):
    implements(IWidgetInputError)
