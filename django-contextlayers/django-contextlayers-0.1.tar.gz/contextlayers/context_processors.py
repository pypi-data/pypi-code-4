#!/usr/bin/env python
# -*- coding: utf-8 -*-
from .models import LayerBase


def layer_tool(request):
    """Applies layers matching the request to a context."""
    path = request.path
    try:
        layer_context = {}
        global_context = {'layers': layer_context}
        for layer in LayerBase.objects.get_available_layers(path):
            layer.contribute_to_context(layer_context, global_context)
        return global_context
    except (Exception, ), exc:
        return {}
