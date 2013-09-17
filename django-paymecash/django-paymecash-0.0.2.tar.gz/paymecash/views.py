# -*- coding: utf-8 -*-

import logging
from django.http import HttpResponse
from django.views.generic import View
from annoying.functions import get_object_or_None
from django.views.decorators.csrf import csrf_exempt
from .models import Payment

logger = logging.getLogger('paymecash')


class Confirm(View):
    @csrf_exempt
    def dispatch(self, *args, **kwargs):
        return super(Confirm, self).dispatch(*args, **kwargs)

    def post(self, request, *args, **kwargs):
        # TODO: здесь нужно проверять хэш данных, которого нет

        # Get payment
        order_id = request.POST.get('order_id')
        payment = get_object_or_None(Payment, order_id=order_id)
        if not payment:
            logger.error('Payment with order_id "%s" was not found' % order_id)
            return HttpResponse()

        # Checking the error message and set if it exist
        message = request.POST.get('message')
        if message:
            payment.result = Payment.RESULT_ERROR
            logger.error('Recieved error message for order_id %s' % order_id)
            return HttpResponse()

        transaction_id = request.POST.get('transaction')
        if transaction_id.isdigit():
            payment.transaction_id = request.POST.get('transaction')
        payment.result = Payment.RESULT_OK
        payment.save()
        logger.info('Payment with order_id "%s" and transaction_id "%s" was confirmed' % (order_id, transaction_id))

        return HttpResponse()