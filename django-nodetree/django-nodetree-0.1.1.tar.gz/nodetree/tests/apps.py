from __future__ import unicode_literals

from django.test import TestCase

import nodetree
from nodetree.exceptions import AlreadyRegistered, NotRegistered

from .nodetypes import PersonNodeType
from .models import Town, Person
from nodetree.settings import nodetree_settings


class TestNodeTree(TestCase):

    def test_register(self):
        self.assertRaises(AlreadyRegistered, nodetree.app.register, PersonNodeType)

    def test_unregister(self):
        nodetree.app.unregister(PersonNodeType)
        self.assertFalse(nodetree.app.has_node_type('person'))

        with self.assertRaises(NotRegistered):
            nodetree.app.unregister(PersonNodeType)

        nodetree.app.register(PersonNodeType)

    def test_get_node_type(self):
        self.assertIsNone(nodetree.app.get_node_type('foo'))
        self.assertEqual(nodetree.app.get_node_type('town'), nodetree.app._map.get('town'))

    def test_has_node_type(self):
        self.assertFalse(nodetree.app.has_node_type('foo'))
        self.assertTrue(nodetree.app.has_node_type('area'))

    def test_get_node_type_for_model(self):
        node_type_obj = nodetree.app.get_node_type('person')
        self.assertEqual(node_type_obj, nodetree.app.get_node_type_for_model(Person))

        person = Person(first_name='Lukas', last_name='Buenger')
        self.assertEqual(node_type_obj, nodetree.app.get_node_type_for_model(person))

    def test_get_generic_field_dict(self):
        generic_field_dict = nodetree.app.get_generic_field_dict()
        self.assertIn(Town, generic_field_dict)
        self.assertIsInstance(generic_field_dict[Town], nodetree_settings.DEFAULT_CONTENT_SERIALIZER)

    def test_get_node_serializer_class(self):
        serializer = nodetree.app.get_node_serializer_class()()
        self.assertIn(Town, serializer.fields['content'].serializers)
        self.assertIsInstance(serializer, nodetree_settings.BASE_NODE_SERIALIZER)

    def test_get_update_node_serializer_class(self):
        serializer = nodetree.app.get_update_node_serializer_class()()
        self.assertIsInstance(serializer, nodetree_settings.BASE_UPDATE_NODE_SERIALIZER)

    def test_get_create_node_serializer_class(self):
        serializer = nodetree.app.get_create_node_serializer_class()()
        self.assertIn(Town, serializer.fields['content'].serializers)
        self.assertIsInstance(serializer, nodetree_settings.BASE_CREATE_NODE_SERIALIZER)