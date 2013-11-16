from django import forms
from django.contrib import admin
from buysafe.models import PaymentMethod


class PaymentMethodForm(forms.ModelForm):
    class Meta:
        model = PaymentMethod
        widgets = {
            'password': forms.PasswordInput(render_value=True)
        }


class PaymentMethodAdmin(admin.ModelAdmin):
    list_display = ('is_enabled', 'name', 'payment_type', 'store_id', 'content')
    list_editable = ('is_enabled',)
    list_display_links = ('name',)
    form = PaymentMethodForm


admin.site.register(PaymentMethod, PaymentMethodAdmin)
