from __future__ import unicode_literals

from django.test import TestCase

from nodetree.settings import nodetree_settings
from nodetree.serializers import BaseContentSerializer, BaseNodeSerializer, BaseUpdateNodeSerializer, BaseCreateNodeSerializer

# TODO: Test exception handling
from nodetree.viewsets import BaseContentViewSet, NodeViewSet

class TestNodeTreeSettingsDefault(TestCase):

    def test_default_content_serializer(self):
        self.assertEqual(nodetree_settings.DEFAULT_CONTENT_SERIALIZER, BaseContentSerializer)

    def test_default_content_view_set(self):
        self.assertEqual(nodetree_settings.DEFAULT_CONTENT_VIEW_SET, BaseContentViewSet)

    def test_node_view_set(self):
        self.assertEqual(nodetree_settings.NODE_VIEW_SET, NodeViewSet)

    def test_default_max_depth(self):
        self.assertEqual(nodetree_settings.DEFAULT_MAX_DEPTH, 0)

    def test_base_node_serializer(self):
        self.assertEqual(nodetree_settings.BASE_NODE_SERIALIZER, BaseNodeSerializer)

    def test_base_update_node_serializer(self):
        self.assertEqual(nodetree_settings.BASE_UPDATE_NODE_SERIALIZER, BaseUpdateNodeSerializer)

    def test_base_create_node_serializer(self):
        self.assertEqual(nodetree_settings.BASE_CREATE_NODE_SERIALIZER, BaseCreateNodeSerializer)

    def test_node_permissions(self):
        self.assertEqual(nodetree_settings.NODE_PERMISSIONS, None)