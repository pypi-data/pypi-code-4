# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db.models import Model

from rest_framework.relations import HyperlinkedRelatedField
from rest_framework.routers import DefaultRouter

from nodetree.fields import ContentField, RecursiveRelatedField
from nodetree.maps import SimpleMap
from nodetree.exceptions import AlreadyRegistered, NotRegistered
from nodetree.serializers import BaseNodeSerializer, BaseUpdateNodeSerializer, BaseCreateNodeSerializer, BaseInputNodeSerializer
from nodetree.settings import nodetree_settings
from nodetree.viewsets import NodeViewSet

class NodeTree(object):
    """
    The main NodeTree application that exposes an interface to register, create and retrieve ``NodeType`` objects. It
    acts as registration pool towards your app and as facade for the other members of the NodeTree world e.g. the
    validation procedure of ``BaseUpdateNodeSerializer``.

    It gets instantiated within the same package and as for now behaves as a singleton,
    similar to e.g. the ``django.admin.site`` object. In fact, its interface tries to resemble that of
    ``django.admin.site``.

    .. note::
       If you intend to subclass or extend NodeTree components, please keep in mind, that you should always use
       ``nodetree.app`` to establish communication between different parts of the application (resources, models,
       ``NodeTypes`` and so on) to not break the `Facade pattern <http://en.wikipedia.org/wiki/Facade_pattern>`_.
    """

    def __init__(self):
        """
        Creates an instance of ``nodetree.base.SimpleMap`` to register ``NodeType``s
        """
        self._map = SimpleMap()

    def register(self, node_type):
        """
        With this method you make a ``NodeType`` available for NodeTree. Raises ``nodetree.exceptions.AlreadyRegistered``
        if the given ``NodeType`` is already registered.

        :param node_type: A subclass of ``NodeType``.
        :type node_type: nodetree.nodetypes.NodeType

        :raises: nodetree.exceptions.AlreadyRegistered
        """
        try:
            node_type = node_type()
            self._map.set(node_type.name, node_type)
        except KeyError:
            raise AlreadyRegistered('"%r" is already registered to NodeTree' % node_type)

    def unregister(self, node_type):
        try:
            node_type = node_type()
            self._map.remove(node_type.name)
        except KeyError:
            raise NotRegistered('"%r" is not registered to NodeTree' % node_type)

    def get_node_type(self, node_type_name):
        """
        A shortcut to the ``get`` method of the internal ``nodetree.base.SimpleMap`` object.

        :param node_type_name: A valid name of a ``NodeType`` that has been registered to NodeTree.
        :type node_type_name: str or unicode

        :rtype: nodetree.NodeType

        .. note:
           As for now, this method fails silently if a key doesn't exist. However, this behavior may change in favor of
           a stricter error handling
        """
        return self._map.get(node_type_name)

    def get_node_type_for_model(self, model):

        model_class = None
        if isinstance(model, type):
            model_class = model
        elif isinstance(model, Model):
            model_class = model.__class__

        if model_class is not None:
            for node_type_obj in self._map.values():
                if node_type_obj.model_class == model_class:
                    return node_type_obj
        return None

    def has_node_type(self, node_type_name):
        """
        :param node_type_name: A valid name of a ``NodeType`` that you want to check against.
        :type node_type_name: str or unicode

        :rtype: bool
        """
        return node_type_name in self._map.keys()

    def get_generic_field_dict(self):
        """
        Creates and returns the dictionary for the generated ``nodetree.fields.ContentField``.

        .. note:
           As for now the implementation of ``GenericRelatedField`` is still
           `in revision <https://github.com/tomchristie/django-rest-framework/pull/755>`_.

        :rtype: dict
        """
        generic_field_dict = dict()

        for node_type in self._map.values():
            generic_field_dict[node_type.model_class] = node_type.serializer_class()

        return generic_field_dict

    def get_node_serializer_class(self, depth=nodetree_settings.DEFAULT_MAX_DEPTH):
        """
        Creates and returns a subclass of ``BaseNodeSerializer`` with a ``ContentField`` that has a mapping for
        all models registered to NodeTree.

        :rtype: nodetree.serializer.BaseNodeSerializer
        """

        class NodeSerializer(BaseNodeSerializer):
            app = self
            content = ContentField(self.get_generic_field_dict(), read_only=True)
            children = RecursiveRelatedField(many=True, max_depth=depth,
                leaf_serializer=HyperlinkedRelatedField(view_name='node-detail', many=True))
        return NodeSerializer

    def get_update_node_serializer_class(self, depth=nodetree_settings.DEFAULT_MAX_DEPTH):
        """
        Returns ``BaseUpdateNodeSerializer``.

        :rtype: nodetree.serializer.BaseUpdateNodeSerializer
        """
        class UpdateNodeSerializer(BaseUpdateNodeSerializer):
            max_depth = depth
        return UpdateNodeSerializer

    def get_create_node_serializer_class(self, depth=nodetree_settings.DEFAULT_MAX_DEPTH):
        """
        Creates and returns a subclass of ``BaseCreateNodeSerializer`` with a ``ContentField`` that has a mapping for
        all models registered to NodeTree.

        :rtype: nodetree.serializer.BaseCreateNodeSerializer
        """
        class CreateNodeSerializer(BaseCreateNodeSerializer):
            max_depth = depth
            content = ContentField(self.get_generic_field_dict(), required=True)
        return CreateNodeSerializer


    @property
    def urls(self):
        router = DefaultRouter()
        router.register(r'node', NodeViewSet)
        for node_type in self._map.values():
            router.register(r'%s' % node_type.name, node_type.view_set)
        return router.urls


app = NodeTree()