# -*- coding: utf-8 -*-

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'paymentcash',
    }
}

PAYMECASH_WALLET_ID = '000000001060'
PAYMECASH_DEFAULT_CURRENCY = 'RUB'
PAYMECASH_SECRET_KEY = '1d43a7561b5cb5af7877994ee1dc'
PAYMECASH_HIDE_FORM = False