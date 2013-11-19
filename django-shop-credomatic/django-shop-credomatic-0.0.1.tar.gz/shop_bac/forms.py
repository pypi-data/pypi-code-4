# -*- coding: utf-8 -*-
import hashlib

from django.conf import settings
from django.core.exceptions import ValidationError
from django_creditcard.fields import CreditCardField, ExpiryDateField, VerificationValueField
from crispy_forms.layout import Submit, Layout, Div, Row, Column, Field
from crispy_forms.helper import FormHelper
from django import forms
import logging

logger = logging.getLogger(__name__)

AVSRESPONSE_CHOICES = (
    ('X', 'Exact match, 9-character numeric ZIP'),
    ('Y', 'Exact match, 5-character numeric ZIP'),
    ('D', '“'),
    ('M', '“'),
    ('A', 'Address match only'),
    ('B', '“'),
    ('W', '9-character numeric ZIP match only'),
    ('Z', '5-character Zip match only'),
    ('P', '“'),
    ('L', '“'),
    ('N', 'No address or ZIP match'),
    ('C', '“'),
    ('U', 'Address unavailable'),
    ('G', 'Non-U.S. Issuer does not participate'),
    ('I', '“'),
    ('R', 'Issuer system unavailable'),
    ('E', 'Not a mail/phone order'),
    ('S', 'Service not supported'),
    ('0', 'AVS Not Available'),
    ('O', '“'),
    ('B', '“'),
)

CVVRESPONSE_CHOICES = (
    ('M', 'CVV2/CVC2 Match'),
    ('N', 'CVV2/CVC2 No Match'),
    ('P', 'Not Processed'),
    ('S', 'Merchant has indicated that CVV2/CVC2 is not present on card'),
    ('U', 'Issuer is not certified and/or has not provided Visa encryption keys'),
)

RESPONSE_CODE_CHOICES = (
    (100, 'Transaction was Approved'),
    (200, 'Transaction was Declined by Processor'),
    (220, 'Incorrect Payment Data'),
    (240, 'Call Issuer for Further Information'),
    (250, 'Pick Up Card'),
    (260, 'Declined with further Instructions Available (see response text)'),
    (300, 'Transaction was Rejected by Gateway'),
    (400, 'Transaction Error Returned by Processor'),
    (410, 'Invalid Merchant Configuration'),
    (420, 'Communication Error'),
    (430, 'Duplicate Transactoin at Processor'),
    (440, 'Processor Format Error'),
    (460, 'Processor Feature not Available'),
)


class PaymentForm(forms.Form):
    CARD_CHOICES = (
        ('VISA', 'Visa'),
        ('MASTERCARD', 'Mastercard'),
        ('AMEX', 'American Express'),
        ('DINERS CLUB', 'Diners Club'),
        ('JCB', 'JCB'),
    )

    fullname = forms.CharField(label="Nombre Tarjetahabiente")
    address1 = forms.CharField(label="Direccion")
    card_number = CreditCardField(
        widget=forms.TextInput(attrs={'autocomplete': 'off'}),
        label="Numero de tarjeta")
    expiry_date = ExpiryDateField(required=True, label="Fecha de expiracion")
    card_code = VerificationValueField(
        widget=forms.TextInput(attrs={'autocomplete': 'off'}),
        label="Codigo tarjeta")
    card_type = forms.ChoiceField(
        choices=CARD_CHOICES,
        required=True,
        label="Tipo de tarjeta"
    )

    def __init__(self, *args, **kwargs):
        super(PaymentForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.html5_required = True
        self.helper.form_method = 'POST'
        self.helper.form_action = '.'
        self.helper.add_input(Submit('submit', 'Proceder'))
        self.helper.layout = Layout(
            Div(
                Row(
                    Column(
                        Field('fullname', css_class='input-large'),
                        css_class='span4',
                    ),
                    Column(
                        Field('address1', css_class='input-large'),
                        css_class='span5',
                    ),
                ),
                Row(
                    Column(
                        Field('card_number', css_class='input-large'),
                        css_class='span4',
                    ),
                    Column(
                        Field('card_code'),
                        css_class='span5',
                    ),
                ),
                Row(
                    Column(
                        Field('expiry_date', css_class='input-small'),
                        css_class='span4',
                    ),
                    Column(
                        Field('card_type'),
                        css_class='span5',
                    ),
                ),
            ),
        )

    def clean(self):
        cd = self.cleaned_data
        return cd

class HiddenPaymentForm(PaymentForm):
    type = forms.CharField(widget=forms.HiddenInput)
    key_id = forms.CharField(widget=forms.HiddenInput)
    hash = forms.CharField(widget=forms.HiddenInput)
    time = forms.CharField(widget=forms.HiddenInput)
    orderid = forms.CharField(widget=forms.HiddenInput)
    redirect = forms.CharField(widget=forms.HiddenInput)
    cvv = forms.CharField(widget=forms.HiddenInput)
    ccnumber = forms.CharField(widget=forms.HiddenInput)
    ccexp = forms.CharField(widget=forms.HiddenInput)
    amount = forms.DecimalField(widget=forms.HiddenInput)

    def __init__(self, *args, **kwargs):
        super(PaymentForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_method = 'POST'
        self.helper.form_action = settings.ECOMMERCE_URL
        self.helper.add_input(Submit('submit', 'Confirmar'))


class CredomaticResponseForm(forms.Form):
    """
    response
    1 = Transaction Approved
    2 = Transaction Declined
    3 = Error in transaction data or system error
    """
    orderid = forms.CharField(widget=forms.HiddenInput)
    amount = forms.DecimalField(widget=forms.HiddenInput)
    response = forms.IntegerField(min_value=1, max_value=3)
    responsetext = forms.CharField()        # Textual response
    authcode = forms.CharField()            # Transaction authorization code
    transactionid = forms.CharField()       # Payment Gateway transaction id
    avsresponse = forms.ChoiceField(choices=AVSRESPONSE_CHOICES)
    hash = forms.CharField()
    cvvresponse = forms.ChoiceField(choices=CVVRESPONSE_CHOICES)
    response_code = forms.ChoiceField(choices=RESPONSE_CODE_CHOICES)

    time = forms.IntegerField()

    def __init__(self, *args, **kwargs):
        super(CredomaticResponseForm, self).__init__(*args, **kwargs)


    def clean(self):
        cd = self.cleaned_data
        if self.is_valid():

            hashed_data = hashlib.md5(
                '%(orderid)s|%(amount)0.2f|%(response)s|%(transactionid)s|%(avsresponse)s|%(cvvresponse)s|%(time)s|%(key)s' % dict(
                    orderid=cd['orderid'],
                    amount=cd['amount'],
                    response=cd['response'],
                    transactionid=cd['transactionid'],
                    avsresponse=cd['avsresponse'],
                    cvvresponse=cd['cvvresponse'],
                    time=cd['time'],
                    key=settings.ECOMMERCE_KEY)).hexdigest()
            if hashed_data != cd['hash']:
                raise ValidationError('hash no valid')
        return cd
