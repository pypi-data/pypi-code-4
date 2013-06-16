from __future__ import unicode_literals

from django.core.exceptions import ImproperlyConfigured
from django.test import TestCase

from rest_framework import serializers

from nodetree.nodetypes import NodeType
from nodetree.serializers import BaseContentSerializer

from .models import Town


class TownSerializer(serializers.ModelSerializer):

    class Meta:
        model = Town


class TestNodeType(TestCase):

    def test_non_existing_name(self):

        class TownNodeType(NodeType):
            pass

        with self.assertRaises(ImproperlyConfigured):
            node_type = TownNodeType()

    def test_invalid_name(self):

        class TownNodeType(NodeType):
            name = 'foooooooooooooooooo-baaaaaaaaaaaaaaar'

        with self.assertRaises(ImproperlyConfigured):
            node_type = TownNodeType()

        class AnotherTownNodeType(NodeType):
                    name = 'FooBar'

        with self.assertRaises(ImproperlyConfigured):
            node_type = AnotherTownNodeType()

    def test_non_existing_model(self):

        class TownNodeType(NodeType):
            name = 'foo-bar'

        with self.assertRaises(ImproperlyConfigured):
            node_type = TownNodeType()

    def test_invalid_model(self):

        class TownNodeType(NodeType):
            name = 'foo-bar'
            model_class = dict

        with self.assertRaises(ImproperlyConfigured):
            node_type = TownNodeType()

    def test_default_serializer(self):

        class TownNodeType(NodeType):
            name = 'foo-bar'
            model_class = Town

        node_type = TownNodeType()
        self.assertTrue(issubclass(node_type.serializer_class, BaseContentSerializer))
        self.assertEqual(node_type.serializer_class.Meta.model, Town)


    def test_any_string(self):

        class TownNodeType(NodeType):
            name = 'foo-bar'
            model_class = Town
            allowed_children = ['any']

        node_type = TownNodeType()
        self.assertTrue(node_type.is_allowed_child('blub'))

    def test_not_any_string(self):

        class TownNodeType(NodeType):
            name = 'foo-bar'
            model_class = Town
            allowed_children = ['foo']

        node_type = TownNodeType()
        self.assertFalse(node_type.is_allowed_child('blub'))

    def test_invalid_custom_serializer(self):

        class TownNodeType(NodeType):
            name = 'foo-bar'
            model_class = Town
            serializer_class = dict

        with self.assertRaises(ImproperlyConfigured):
            node_type = TownNodeType()

    def test_custom_serializer(self):

        class TownNodeType(NodeType):
            name = 'foo-bar'
            model_class = Town
            serializer_class = TownSerializer

        node_type = TownNodeType()
        self.assertEqual(node_type.serializer_class, TownSerializer)