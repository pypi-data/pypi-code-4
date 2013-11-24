# -*- coding: utf-8 -*-

"""Module containing test for resource description."""

from django.utils import unittest

from ui_permissions.descriptor.components import Element, Field
from ui_permissions.descriptor.resource import Resource


class ResourceTestCase(unittest.TestCase):

    """Tests Resource behaviour."""

    class EmptyTestResource(Resource):

        """Empty resource test class."""
        pass

    class TestResource(Resource):

        """Resource test class."""

        test_element = Element.visible()
        test_field = Field.editable()

    def setUp(self):
        self.empty_resource_obj = ResourceTestCase.EmptyTestResource()
        self.resource_obj = ResourceTestCase.TestResource()

    def test_basic_property_presence(self):
        """Check if Resource instance has basic content type properties."""
        self.assertTrue(hasattr(self.empty_resource_obj, 'element'))
        self.assertTrue(hasattr(self.empty_resource_obj, 'field'))

        self.assertTrue(hasattr(self.resource_obj, 'element'))
        self.assertTrue(hasattr(self.resource_obj, 'field'))

    def test_component_get(self):
        """Check if getting component returns something."""
        self.assertIsNotNone(self.resource_obj.element.test_element)
        self.assertIsNotNone(self.resource_obj.field.test_field)

        self.assertIsNotNone(self.resource_obj.element.ghost_test_element)
        self.assertIsNotNone(self.resource_obj.field.ghost_test_field)

        self.assertIsNotNone(self.empty_resource_obj.element.test_element)
        self.assertIsNotNone(self.empty_resource_obj.field.test_field)

    def test_defined_component_state(self):
        """Check if querying defined component returns proper result."""
        self.assertTrue(self.resource_obj.element.test_element.VISIBLE)
        self.assertFalse(self.resource_obj.element.test_element.HIDDEN)

        self.assertTrue(self.resource_obj.field.test_field.EDITABLE)
        self.assertFalse(self.resource_obj.field.test_field.DISABLED)
        self.assertFalse(self.resource_obj.field.test_field.HIDDEN)

    def test_undefined_component_state(self):
        """Check if querying undefined component returns proper default result."""
        self.assertTrue(self.resource_obj.element.ghost_test_element.VISIBLE)
        self.assertFalse(self.resource_obj.element.ghost_test_element.HIDDEN)

        self.assertTrue(self.resource_obj.field.ghost_test_field.EDITABLE)
        self.assertFalse(self.resource_obj.field.ghost_test_field.DISABLED)
        self.assertFalse(self.resource_obj.field.ghost_test_field.HIDDEN)

        self.assertTrue(self.empty_resource_obj.element.test_element.VISIBLE)
        self.assertFalse(self.empty_resource_obj.element.test_element.HIDDEN)

        self.assertTrue(self.empty_resource_obj.field.test_field.EDITABLE)
        self.assertFalse(self.empty_resource_obj.field.test_field.DISABLED)
        self.assertFalse(self.empty_resource_obj.field.test_field.HIDDEN)
