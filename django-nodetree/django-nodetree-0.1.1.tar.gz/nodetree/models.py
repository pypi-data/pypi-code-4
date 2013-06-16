# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib.contenttypes.generic import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.db import models

from mptt.fields import TreeForeignKey
from mptt.models import MPTTModel


class Node(MPTTModel):
    """
    The ``Node`` model is actually nothing more than an inheritor of ``MPTTModel`` with additional fields needed
    to create a generic relation and a ``node_type`` field for easily identifying the related ``NodeType``.
    Every ``BaseContent`` that resides within a tree is tied to a ``Node`` object. The ``Node`` object is only
    responsible for logic that is related to tree structure and modification.

    For more information about the inner workings of the tree implementation, please visit
    `Django MPTT's Documentation <http://django-mptt.readthedocs.org/en/latest/models.html#models-and-managers>`_.
    """

    # Generic relation fields
    content_type = models.ForeignKey(ContentType, null=True)
    object_id = models.PositiveIntegerField(null=True)
    content = GenericForeignKey()

    # MPTT parent field
    parent = TreeForeignKey('self', null=True, blank=True, related_name='children')

    # Node type field
    node_type = models.SlugField(max_length=31)

    def __unicode__(self):
        return '%s: %s %d' % ('Node', self.content, self.pk or 0)

    def delete(self, force_delete_content=True, *args, **kwargs):
        """
        This deletes the ``Node`` object. Tree adjustments are again handled by MPTT.

        :param force_delete_content: If set to ``False`` the related ``BaseContent`` object will not get deleted.
        :type force_delete_content: bool

        .. note::
            Please note that you should not set ``force_delete_content`` to ``False`` unless you have a good
            reason to keep your content objects for further use.

        """
        if force_delete_content:
            self.content.delete()
        super(Node, self).delete(*args, **kwargs)

    class Meta:
        # Make sure that it's impossible to connect two ``Node`` objects with the same ``BaseContent``.
        unique_together = (('content_type', 'object_id'),)


class BaseContent(models.Model):
    """
    As for now the abstract ``BaseContent`` model provides only basic features to establish a reverse relation
    to its ``Node`` object. It still should be used as parent class for all models you want to register with NodeTree,
    because of possible future changes to the ``BaseContent`` implementation.
    """
    nodes = GenericRelation(Node)

    @property
    def node(self):
        """
        :returns: ``nodetree.models.Node`` -- The related ``Node`` object if existing, else ``None``
        """
        if self.nodes.count() > 0:
            return self.nodes.all()[0]
        else:
            return None

    class Meta:
        abstract = True