#!/usr/bin/env python
# -*- coding: utf-8 -*-
from fnmatch import translate

from django.db import models
from django.db.models.signals import class_prepared
from django.dispatch import receiver
from django.utils.translation import ugettext as _

from .managers import LayerManager


@receiver(class_prepared)
def register_layer_provider(sender, **kwargs):
    """Registers layer provider model classes with the manager."""
    if getattr(sender, 'LayerMeta', False):
        LayerManager.register(sender)


class LayerBase(models.Model):
    """Abstract model for layers.

    Subclasses must reimplement the `contribute_to_context` method, and in that
    method, manipulate one or both context dictionaries supplied by the context
    processor.

    """
    name = models.CharField(_('name'), max_length=64, db_index=True,
        unique=True, help_text=_("""The name of this layer."""))

    path = models.CharField(_('path'), db_index=True, max_length=128,
        unique=True, help_text=_("""Path to match to select this layer."""))

    path_rx = models.CharField(_('path rx'), db_index=True, max_length=128,
        help_text=_("""Regular expression computed from the path."""))

    available_start = models.DateTimeField(_('available start'), db_index=True,
        blank=True, null=True, help_text=_("""
        Date and time when this layer becomes available.  If empty, the layer
        will always be available (unless the stop date is in the past).
        """))

    available_stop = models.DateTimeField(_('available stop'), db_index=True,
        blank=True, null=True, help_text=_("""
        Date and time when this layer stops being available.  If empty, the
        layer will always be available (unless the start date is in the
        future).
        """))

    order = models.IntegerField(_('order'), default=1,
        help_text=_("""Order of this layer within all available layers."""))

    objects = LayerManager()

    class Meta:
        abstract = True

    def __unicode__(self):
        return self.name

    def compute_rx(self, value):
        """Returns a regular expression string from the given glob pattern.

        The returned pattern always has "^" at the beginning and "/$" at the
        end.  Subclasses can reimplement this method as necessary.

        """
        # The '\Z(?ms)' on the end causes invalid queries in postgres,
        # so we remove it:
        value = translate(value)[:-7]
        if not value.startswith('^'):
            value = '^' + value
        if not value.endswith('$'):
            if not value.endswith('/'):
                value += '/'
            value += '$'
        return value

    def contribute_to_context(self, layer_context, global_context):
        """The layers context processor calls this method on available layers.

        The layer context is a mapping available to the template at "layer".
        The global context is the mapping returned by the processor.  The global
        context contains the layer context.

        Subclasses must provide an implementation.

        """
        raise NotImplementedError('Layer subclasses must provide this method')

    def save(self, *args, **kwargs):
        """Overwrites the path_rx field before save."""
        self.path_rx = self.compute_rx(self.path)
        super(LayerBase, self).save(*args, **kwargs)
