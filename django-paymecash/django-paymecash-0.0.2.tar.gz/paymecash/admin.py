# -*- coding: utf-8 -*-

from django.contrib import admin
from .models import Payment


class PaymentAdmin(admin.ModelAdmin):
    list_display = ('order_id', 'result', 'wallet_id', 'product_price',
                    'product_currency', 'payment_type_group_id', 'transaction_id', 'created')
    list_filter = ('wallet_id', 'payment_type_group_id', 'result', 'created')
    search_fields = ('order_id', 'transaction_id', 'cs1', 'cs2', 'cs3')

admin.site.register(Payment, PaymentAdmin)