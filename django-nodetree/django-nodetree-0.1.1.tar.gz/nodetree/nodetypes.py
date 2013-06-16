# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import re

from django.db import models
from django.core.exceptions import ImproperlyConfigured

from rest_framework.serializers import Serializer

from nodetree.settings import nodetree_settings


NAME_PATTERN = re.compile(r'[\-]*\w{1,31}')

#TODO: Write proper representation functions for all items

class NodeType(object):
    """
    With subclasses of ``NodeType`` you define and hook up all parts that are needed to establish a NodeTree entity.
    It's also the object you'll register to the ``NodeTree`` app.
    """

    name = None
    """
    A unique name for this ``NodeType``. Can only contain small characters and minus symbols (``r'[\-]*\w')``. This
    property has to be set for each subclass, otherwise ``ImproperlyConfigured`` is raised.

    .. note::
       This will be the main identifier for the associated ``model_class`` within the whole NodeTree world.
    """

    model_class = None
    """
    The content model you want to use with this ``NodeType``. Subclass of ``BaseContent``. This property has to be
    set for each subclass, otherwise ``ImproperlyConfigured`` is raised.
    """

    serializer_class = None
    """
    A ``Serializer`` class or subclass that should get used to expose the ``model_class`` to the NodeTree API.
    By default ``nodetree_settings.DEFAULT_CONTENT_SERIALIZER`` is used.
    """

    view_set_class = None

    allowed_children = []
    """
    A list of ``NodeType`` names that are allowed to be added as children to a node of this type. If the list is empty,
    the ``NodeType`` behaves as if the ``is_leaf`` property is set to ``True``.
    """

    forbidden_children = []

    is_root = False
    """
    If ``True`` this ``NodeType`` can be created without a parent node or moved to a root position.
    """

    is_leaf = False
    """
    Adding child nodes to objects of this ``NodeType`` will not be allowed. ``allowed_children`` will be ignored
    if ``is_leaf`` is ``True``.
    """

    def __init__(self):
        """
         :raises: django.core.exceptionsImproperlyConfigured
        """

        if self.name is None:
            raise ImproperlyConfigured("'%r' has to have its 'name' property set." % self.__class__)
        elif not NAME_PATTERN.match(self.name):
            raise ImproperlyConfigured("'%r' has an invalid 'name' property." % self.__class__)

        if self.model_class is None:
            raise ImproperlyConfigured("'%r' has to have its 'model_class' property set." % self.__class__)
        elif not issubclass(self.model_class, models.Model):
            raise ImproperlyConfigured("'%r' has an invalid 'model_class'." % self.__class__)

        if self.serializer_class is None:
            class DefaultSerializer(nodetree_settings.DEFAULT_CONTENT_SERIALIZER):
                class Meta:
                    model = self.model_class
            self.serializer_class = DefaultSerializer
        elif not issubclass(self.serializer_class, Serializer):
            raise ImproperlyConfigured("'%r' has an invalid 'serializer_class'." % self.__class__)

    def is_allowed_child(self, name):
        return self.is_leaf is not True and \
               (len(self.forbidden_children) > 0 and name not in self.forbidden_children or \
               nodetree_settings.ANY_KEYWORD in self.allowed_children or \
               name in self.allowed_children)

    @property
    def view_set(self):
        view_set_class = self.view_set_class or nodetree_settings.DEFAULT_CONTENT_VIEW_SET
        class ContentViewSet(view_set_class):
            serializer_class = self.serializer_class or nodetree_settings.DEFAULT_CONTENT_SERIALIZER
            queryset = self.model_class.objects.all()
        return ContentViewSet


    def __repr__(self):
        return '<NodeType: %s>' % self.name