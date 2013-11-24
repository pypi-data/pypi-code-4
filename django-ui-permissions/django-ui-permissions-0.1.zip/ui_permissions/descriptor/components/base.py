# -*- coding: utf-8 -*-

"""Module containing base for all component classes."""


class ComponentMeta(type):

    """Component meta class."""

    def __new__(cls, name, bases, attrs):
        for index, state_name in enumerate(attrs['states']):
            attrs[state_name] = index
        return super(ComponentMeta, cls).__new__(cls, name, bases, attrs)


class Component(object):

    """Component class."""

    __metaclass__ = ComponentMeta

    states = ()
    state_id = None

    def __init__(self, state_id):
        self.state_id = state_id

    @property
    def state(self):
        """Name of the current component state."""
        return self.states[self.state_id]
