#!/usr/bin/env python
# -*- coding: utf-8 -*-
from datetime import datetime

from django.contrib import admin


class LayerAdmin(admin.ModelAdmin):
    """Base class for Layer admin."""
    list_display = ('id', 'name', 'path', 'is_available',
        'available_start', 'available_stop', 'order', )
    list_filter = ('path', 'available_start', 'available_stop', )
    ordering = ('-order', )
    readonly_fields = ('path_rx', )

    def is_available(self, obj):
        """True if this layer is available to the context processor."""
        now = datetime.now()
        start, stop = obj.available_start, obj.available_stop
        return (start is None or start <= now) and (stop is None or stop >= now)
    is_available.boolean = True
