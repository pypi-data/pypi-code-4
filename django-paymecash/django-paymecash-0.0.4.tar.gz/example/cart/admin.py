# -*- coding: utf-8 -*-

from django.contrib import admin
from .models import Goods
from .models import Order


class GoodsInLine(admin.StackedInline):
    extra = 0
    model = Goods

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_id', 'amount')

    inlines = (GoodsInLine,)

admin.site.register(Order, OrderAdmin)