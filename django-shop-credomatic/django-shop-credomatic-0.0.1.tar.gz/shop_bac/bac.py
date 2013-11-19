#-*- coding: utf-8 -*-
from decimal import Decimal
import time
import logging
import hashlib

from django.conf import settings
from django.conf.urls.defaults import patterns, url
from django.contrib.sites.models import Site
from django.core.urlresolvers import reverse
from django.db import transaction
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.views.decorators.csrf import csrf_exempt
from shop.models import Order
from .forms import PaymentForm, HiddenPaymentForm, CredomaticResponseForm
from shop.util.order import get_order_from_request
from .models import OrderBacResponse

class CreditCardBackend(object):
    backend_name = "Tarjeta Credito/Debito"
    url_namespace = "creditcard"

    #===========================================================================
    # Defined by the backends API
    #===========================================================================

    def __init__(self, shop):
        self.shop = shop
        self.logger = logging.getLogger('transaction')
        assert len(settings.ECOMMERCE_KEY_ID) >= 7, \
            "ECOMMERCE_PUBLIC_KEY must contain at least 7 characters"

    def get_urls(self):
        urlpatterns = patterns('',
                               url(r'^$', self.view_that_asks_for_money, name='creditcard'),
                               url(r'^final$', self.view_that_receive_response, name='final'),
        )
        return urlpatterns

    def get_form(self, request):
        form = PaymentForm()
        return form

    #===========================================================================
    # Views
    #===========================================================================

    @csrf_exempt
    def view_that_asks_for_money(self, request):
        form = self.get_form(request)
        order = get_order_from_request(request)
        template = 'shop_bac/payment.html'
        if request.method == 'POST':
            form = PaymentForm(request.POST)
            if form.is_valid():
                template = 'shop_bac/confirm_payment.html'
                payment_data = self.get_context(request, order.id, form)
                self.logger.info('Order: {0}, Amount: {1}, Shipping: {2}'.format(order, payment_data['amount'], order.shipping_costs ))
                form = HiddenPaymentForm(payment_data)
                self.logger.info('PaymentData: {0}'.format(payment_data))
        context = {'form': form}
        rc = RequestContext(request, context)
        return render_to_response(template, rc)

    @csrf_exempt
    def view_that_receive_response(self, request):
        template = 'shop_bac/success.html'
        order = get_order_from_request(request)
        aprobado = False
        if request.method == 'GET':
            form = CredomaticResponseForm(request.GET)
            self.logger.info('CredomaticResponse: {0}'.format(request.GET))
            with transaction.commit_on_success():
                if form.is_valid():
                    cd = form.cleaned_data
                    orden = Order.objects.get(pk=cd['orderid'])
                    if int(cd['response']) == 1:
                        aprobado = True
                        self.shop.confirm_payment(
                            orden,
                            cd['amount'],
                            cd['transactionid'],
                            self.backend_name)
                    else:
                        aprobado = False
                    OrderBacResponse.objects.create(
                        order=orden,
                        amount=Decimal(cd['amount']),
                        response=cd['response'],
                        responsetext=cd['responsetext'],
                        authcode=cd['authcode'],
                        transactionid=cd['transactionid'],
                        avsresponse=cd['avsresponse'],
                        hash=cd['hash'],
                        cvvresponse=cd['cvvresponse'],
                        response_code=cd['response_code'],
                    )
                else:
                    self.logger.info('TRANSACCION DENEGADA: orden:{0}'.format(order.id))

        self.logger.info('====================================================================================')
        context = {'aprobado': aprobado, 'order': order}
        rc = RequestContext(request, context)
        return render_to_response(template, rc)


    def get_context(self, request, order, form):
        cd = form.cleaned_data
        amount = get_order_from_request(request).order_total
        domain = Site.objects.get_current().domain
        epoch = int(time.time())
        protocol = 'http' if settings.DEBUG else 'https'
        hash = self.make_hash(order, amount, epoch)
        return {
            'orderid': order,
            'fullname':         cd['fullname'],
            'address1':         cd['address1'],
            'card_number':      cd['card_number'],
            'card_code':        cd['card_code'],
            'card_type':        cd['card_type'],
            'cvv':              cd['card_code'],
            'ccnumber':         cd['card_number'],
            'expiry_date_0':    cd['expiry_date'].month,
            'expiry_date_1':    cd['expiry_date'].year,
            'ccexp':            cd['expiry_date'].strftime('%m%y'),
            'amount':           '%0.2f' % (float(amount)),
            'type':             'auth',
            'key_id':           settings.ECOMMERCE_KEY_ID,
            'hash':             hash,
            'time':             epoch,
            'redirect':         '{protocol}://{domain}{url}'.format(
                protocol=protocol,
                domain=domain,
                url=reverse('final')
            ),
        }

    def make_hash(self, orderid, amount, epoch):
        hashstring = u'%(orderid)s|%(amount)s|%(time)d|%(key)s' % {
            'orderid': orderid,
            'amount': '%0.2f' % (float(amount)),
            'time': epoch,
            'key': settings.ECOMMERCE_KEY
        }
        return hashlib.md5(hashstring).hexdigest()
