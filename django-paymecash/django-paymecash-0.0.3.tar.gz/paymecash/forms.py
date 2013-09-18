# -*- coding: utf-8 -*-

import conf
from django import forms
from .common import get_sign
from .models import Payment


class PayForm(forms.ModelForm):
    FIELDS_FOR_SIGN = ('wallet_id', 'product_price', 'product_currency', 'order_id')

    sign = forms.CharField(widget=forms.HiddenInput())

    def __init__(self, *args, **kwargs):
        super(PayForm, self).__init__(*args, **kwargs)

        data = {
            'wallet_id': self.fields['wallet_id'].initial,
            'product_price': self.fields['product_price'].initial,
            'product_currency': self.fields['product_currency'].initial,
            'order_id': self.fields['order_id'].initial,
        }
        data.update(self.initial)
        self.fields['sign'].initial = get_sign(data)

        if conf.PAYMECASH_HIDE_FORM:
            for name in self.fields:
                self.fields[name].widget = forms.HiddenInput()
        else:
            self.fields['wallet_id'].widget.attrs['readonly'] = True
            self.fields['product_price'].widget.attrs['readonly'] = True
            self.fields['order_id'].widget.attrs['readonly'] = True

    class Meta:
        model = Payment
        fields = ('wallet_id', 'order_id', 'product_price', 'product_currency',
                  'cs1', 'cs2', 'cs3', 'payment_type_group_id')