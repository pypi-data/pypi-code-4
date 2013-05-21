#!/usr/bin/env python
# -*- coding: utf-8 -*-
from collections import OrderedDict
from datetime import datetime

from django.db import connections
from django.db.models import Manager, Q


class LayerManager(Manager):
    """Object manager for Layer models.

    The context processor uses this manager (via LayerBase.objects) to select
    available layers for a request path.

    The models module wires the model class_prepared signal to the register
    method to programmatically register LayerBase subclasses as they're defined.

    """
    models = OrderedDict()

    @classmethod
    def register(cls, model):
        """Add the given model to the layer model registry."""
        cls.models[model] = True

    def get_available_layers(self, path):
        """Generator that yields available layers for registered models."""

        now = datetime.now()
        for model in self.models:
            query = model.objects
            query = query.filter(
                Q(available_start__isnull=True) | Q(available_start__lte=now))
            query = query.filter(
                Q(available_stop__isnull=True) | Q(available_stop__gte=now))

            # This bit is a little crazy.  We can't use
            # query.filter(field__like=value) because we
            # need to use the value of the field (the regex)
            # as the expression on the query.  Instead, we
            # lookup the regex operator for the database connection
            # that the query is using, jigger it a bit, and use
            # it for a manual 'where' clause.  This has been tested
            # with postgresql and sqlite.  YMMV.
            op = connections[query.db].operators['regex']
            op = op.replace('%s', '').strip()
            query = query.extra(
                where=['%s ' + op + ' path_rx'], params=[path])

            for layer in query.order_by('order'):
                yield layer
