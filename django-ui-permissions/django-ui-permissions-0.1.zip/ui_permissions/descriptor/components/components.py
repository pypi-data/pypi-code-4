# -*- coding: utf-8 -*-

"""Module containing main component classes."""

from ui_permissions.descriptor.components.base import Component


class Element(Component):

    """Describes state of web page element."""

    states = ('VISIBLE', 'HIDDEN')

    @classmethod
    def visible(cls):
        return cls(cls.VISIBLE)

    @classmethod
    def hidden(cls):
        return cls(cls.HIDDEN)


class Field(Component):

    """Describes state of form field."""

    states = ('EDITABLE', 'DISABLED', 'HIDDEN')

    @classmethod
    def editable(cls):
        return cls(cls.EDITABLE)

    @classmethod
    def disabled(cls):
        return cls(cls.DISABLED)

    @classmethod
    def hidden(cls):
        return cls(cls.HIDDEN)

    @classmethod
    def excluding_states(cls):
        return [cls.DISABLED, cls.HIDDEN]

    @property
    def exclude(self):
        return self.state_id in self.excluding_states()
