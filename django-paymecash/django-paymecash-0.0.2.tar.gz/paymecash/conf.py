# -*- coding: utf-8 -*-

from django.conf import settings

PAYMECASH_WALLET_ID = getattr(settings, 'PAYMECASH_WALLET_ID')
PAYMECASH_DEFAULT_CURRENCY = getattr(settings, 'PAYMECASH_DEFAULT_CURRENCY', 'RUB')
PAYMECASH_SECRET_KEY = getattr(settings, 'PAYMECASH_SECRET_KEY')
PAYMECASH_PAYMENT_URL = getattr(settings, 'PAYMECASH_PAYMENT_URL', 'https://paymecash.me/api/payment')
PAYMECASH_HIDE_FORM = getattr(settings, 'PAYMECASH_HIDE_FORM', True)