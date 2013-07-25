#!/usr/bin/env python
# -*- coding: utf-8 -*-
from django import forms
from django.conf import settings
from django.utils.safestring import mark_safe
from django_moip.html.conf import *
from django_moip.html.widgets import ValueHiddenInput, ReservedValueHiddenInput
from django_moip.html.conf import (POSTBACK_ENDPOINT, SANDBOX_POSTBACK_ENDPOINT, 
    RECEIVER_EMAIL)

from furl import furl


# 20:18:05 Jan 30, 2009 PST - PST timezone support is not included out of the box.
# MOIP_DATE_FORMAT = ("%H:%M:%S %b. %d, %Y PST", "%H:%M:%S %b %d, %Y PST",)
# MoIP dates have been spotted in the wild with these formats, beware!
MOIP_DATE_FORMAT = ("%H:%M:%S %b. %d, %Y PST",
                      "%H:%M:%S %b. %d, %Y PDT",
                      "%H:%M:%S %b %d, %Y PST",
                      "%H:%M:%S %b %d, %Y PDT",)

class MoipPaymentsForm(forms.Form):
    """
    Creates a MoIP HTML Integration "Pay" button, configured for a
    selling a single item with no shipping.
    
    For a full overview of all the fields you can set (there is a lot!) see:
    https://www.moip.com.br/AdmCheckout.do?method=manual
    
    Usage:
    >>> f = MoipPaymentsForm(initial={'nome':'Widget 001', ...})
    >>> f.render()
    u'<form action="https://www.moip.com.br/PagamentoMoIP.do" method="post"> ...'
    
    """    
    SHIPPING_CHOICES = ((0, "No shipping"), (1, "Shipping"))
    NO_NOTE_CHOICES = ((1, "No Note"), (0, "Include Note"))

    BUY = 'buy'
    SUBSCRIBE = 'subscribe'
    DONATE = 'donate'

    # Where the money goes.
    id_carteira = forms.CharField(widget=ValueHiddenInput(), initial=RECEIVER_EMAIL, max_length=45) # up to 45chr
    
    # Item information.
    valor = forms.IntegerField(widget=ValueHiddenInput()) # up to 9chr
    nome = forms.CharField(widget=ValueHiddenInput(), max_length=64)

    # Recommended but optional
    # (Note: 'id_transacao' will be available to the NIT control if provided)
    descricao = forms.CharField(widget=ValueHiddenInput(), required=False, max_length=256)
    id_transacao = forms.CharField(widget=ValueHiddenInput(), required=False, max_length=32)

    # Optional fields
    frete = forms.ChoiceField(widget=forms.HiddenInput(), choices=SHIPPING_CHOICES, 
        initial=SHIPPING_CHOICES[0][0], required=False) #, max_length=1)
    peso_compra = forms.IntegerField(widget=ValueHiddenInput(), required=False) #, max_length=9)
    pagador_nome = forms.CharField(widget=ValueHiddenInput(), required=False, max_length=90)
    pagador_email = forms.CharField(widget=ValueHiddenInput(), required=False, max_length=45)
    pagador_telefone = forms.IntegerField(widget=ValueHiddenInput(), required=False) #, max_length=10)
    pagador_logradouro = forms.CharField(widget=ValueHiddenInput(), required=False, max_length=45)
    pagador_numero = forms.IntegerField(widget=ValueHiddenInput(), required=False) #, max_length=9)
    pagador_complemento = forms.CharField(widget=ValueHiddenInput(), required=False, max_length=45)
    pagador_bairro = forms.CharField(widget=ValueHiddenInput(), required=False, max_length=45)
    pagador_numero = forms.IntegerField(widget=ValueHiddenInput(), required=False) #, max_length=9)
    pagador_complemento = forms.CharField(widget=ValueHiddenInput(), required=False, max_length=45)
    pagador_bairro = forms.CharField(widget=ValueHiddenInput(), required=False, max_length=45)
    pagador_cep = forms.CharField(widget=ValueHiddenInput(), required=False) #, max_length=8)
    pagador_cidade = forms.CharField(widget=ValueHiddenInput(), required=False, max_length=32)
    #pagador_estado = forms.CharField(widget=ValueHiddenInput(), required=False, max_length=2)
    pagador_pais = forms.CharField(widget=ValueHiddenInput(), required=False, max_length=32)
    pagador_cpf = forms.IntegerField(widget=ValueHiddenInput(), required=False) #, max_length=11)
    pagador_celular = forms.IntegerField(widget=ValueHiddenInput(), required=False) #, max_length=10)
    pagador_sexo = forms.CharField(widget=ValueHiddenInput(), required=False, max_length=1)
    pagador_data_nascimento = forms.IntegerField(widget=ValueHiddenInput(), required=False) #, max_length=8)

    def __init__(self, button_type="buy", *args, **kwargs):
        super(MoipPaymentsForm, self).__init__(*args, **kwargs)
        self.button_type = button_type

    def render(self):
        return mark_safe(u"""<form action="%s" method="post">
    %s
    <input type="image" src="%s" border="0" name="submit" alt="Pagar" />
</form>""" % (POSTBACK_ENDPOINT, self.as_p(), self.get_image()))

    def get_link(self, sandbox=False):
        """ As MoIP accepts GET requests too, the form can be used as a link,
        as if it had been submitted
        """

        if not self.is_valid():
            raise RuntimeError('Please check your MoIP settings and try again.', self.errors) # should never occur

        data = dict([(k,unicode(v).encode('latin-1')) for k,v in self.cleaned_data.items() if v])
        if sandbox:
            f = furl(SANDBOX_POSTBACK_ENDPOINT)
        else:
            f = furl(POSTBACK_ENDPOINT)

        link = f.add(data).url
        return link
        
    def sandbox(self):
        return mark_safe(u"""<form action="%s" method="post">
    %s
    <input type="image" src="%s" border="0" name="submit" alt="Pagar" />
</form>""" % (SANDBOX_POSTBACK_ENDPOINT, self.as_p(), self.get_image()))
        
    def get_image(self):
        return {
            (True, self.SUBSCRIBE): SUBSCRIPTION_SANDBOX_IMAGE,
            (True, self.BUY): SANDBOX_IMAGE,
            (True, self.DONATE): DONATION_SANDBOX_IMAGE,
            (False, self.SUBSCRIBE): SUBSCRIPTION_IMAGE,
            (False, self.BUY): IMAGE,
            (False, self.DONATE): DONATION_IMAGE,
        }[TEST, self.button_type]

    def is_transaction(self):
        return not self.is_subscription()

    def is_donation(self):
        return self.button_type == self.DONATE

    def is_subscription(self):
        return self.button_type == self.SUBSCRIBE


class MoipHtmlBaseForm(forms.ModelForm):
    """Form used to receive and record MoIP NIT/Redirector."""
    # MoIP dates have non-standard formats.
    time_created = forms.DateTimeField(required=False, input_formats=MOIP_DATE_FORMAT)
    payment_date = forms.DateTimeField(required=False, input_formats=MOIP_DATE_FORMAT)
    next_payment_date = forms.DateTimeField(required=False, input_formats=MOIP_DATE_FORMAT)
    subscr_date = forms.DateTimeField(required=False, input_formats=MOIP_DATE_FORMAT)
    subscr_effective = forms.DateTimeField(required=False, input_formats=MOIP_DATE_FORMAT)
