# -*- coding: utf-8 -*-

from mock import patch
from django_webtest import WebTest
from paymecash.common import get_sign
from paymecash.common import get_order_id
from django.core.urlresolvers import reverse
from django.test.utils import override_settings
from .models import Payment


class CommonTests(WebTest):
    @override_settings(PAYMECASH_SECRET_KEY='1d43a7561b5cb5af7877994ee1dc')
    def test_get_sign(self):
        sign = get_sign({
            'product_price': 100.0,
            'wallet_id': '000000001060',
            'product_currency': 'RUB'
        })
        self.assertEqual(sign, '804ed09695d4dd1597d9eb1d9b876606', 'Sign is not equals')

    @patch('uuid.uuid4', lambda: '52bdd583-10da-4115-9479-883198df9f48')
    def test_get_order_id(self):
        order_id = get_order_id()
        self.assertEqual(order_id, '52bdd58310da4115', 'Order ID is not equals')


class PaymentTest(WebTest):
    def test_succes_confirm(self):
        payment = Payment(
            order_id='123',
            wallet_id=123,
            product_price=100.,
        )
        payment.save()

        data = {
            'transaction': '9120',
            'order_id': payment.order_id,
            'message': '',
        }
        url = reverse('paymentcash_confirm')
        self.app.post(url, params=data)

        self.assertEqual(payment.transaction_id, data['transaction'], 'Transaction ID was not set')
        self.assertEqual(payment.result, Payment.RESULT_OK, 'Result is not OK')

    def test_error_confirm(self):
        payment = Payment(
            order_id='123',
            wallet_id=123,
            product_price=100.,
        )
        payment.save()

        data = {
            'transaction': '9120',
            'order_id': 'fail_order',
            'message': '',
        }
        url = reverse('paymentcash_confirm')
        self.app.post(url, params=data)

        self.assertNotEqual(payment.transaction_id, data['transaction'], 'Transaction ID was set at fail order')
        self.assertEqual(payment.result, Payment.RESULT_ERROR, 'Result is not ERROR')