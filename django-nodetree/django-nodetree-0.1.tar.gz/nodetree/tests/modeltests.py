from django.contrib.contenttypes.models import ContentType
from django.db import IntegrityError
from django.test import TestCase

from nodetree.models import Node
from .models import Person


class TestNodeAndBaseContent(TestCase):

    def setUp(self):
        self.content = Person(first_name='Lukas', last_name='Buenger')
        self.content.save()
        self.content_type = ContentType.objects.get_for_model(self.content)

    def test_content_node_property(self):
        self.assertIsNone(self.content.node)

    def test_empty_node(self):
        node = Node()
        node.save()
        self.assertIsNone(node.content)

    def test_reverse_relation(self):

        node = Node(content_type=self.content_type, object_id=self.content.pk)
        node.save()

        # Test reference content -> node
        self.assertEqual(self.content.node, node)

    def test_unique_together(self):

        node = Node(content_type=self.content_type, object_id=self.content.pk)
        node.save()

        second_node = Node(content_type=self.content_type, object_id=self.content.pk)

        self.assertRaises(IntegrityError, second_node.save)

    def test_delete_with_content(self):

        node = Node(content_type=self.content_type, object_id=self.content.pk)
        node.save()
        node.delete()
        self.assertEqual(Person.objects.count(), 0)

    def test_delete_node_only(self):

        node = Node(content_type=self.content_type, object_id=self.content.pk)
        node.save()
        node.delete(force_delete_content=False)
        self.assertEqual(Person.objects.count(), 1)