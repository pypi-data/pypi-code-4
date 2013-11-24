# -*- coding: utf-8 -*-

"""Module containing components tests."""

from django.utils import unittest

from ui_permissions.descriptor.components import Element, Field


class ElementTestCase(unittest.TestCase):

    """Test for checking proper Element class initialization."""

    def test_states_presence(self):
        """Check if class has all declared states."""
        for state_name in Element.states:
            self.assertTrue(hasattr(Element, state_name), state_name)


class FieldTestCase(unittest.TestCase):

    """Test for checking proper Field class initialization."""

    def test_states_presence(self):
        """Check if class has all declared states."""
        for state_name in Field.states:
            self.assertTrue(hasattr(Field, state_name), state_name)
