# /usr/bin/env python
# coding=utf-8
"""A Python module to create more fine-grained matching objects than, for example, mock's ANY object.
"""
from formencode.validators import *


class AnyValid(object):
    def __init__(self, validator):
        self.validator = validator

    def __eq__(self, other):
        try:
            self.validator.to_python(other)
        except Invalid:
            return False

        return True

    def __repr__(self):
        return '{0}({1})'.format(self.__class__.__name__, repr(self.validator))
