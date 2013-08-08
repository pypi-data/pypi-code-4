# -*- coding: utf-8 -*-

from django.conf import settings

SMSCOIN_TARIFF_BASE_PATH = getattr(settings, "SMSCOIN_TARIFF_PATH", "http://key.smscoin.com/xml2/key/%s/")

SMSCOIN_VALIDATOR_PATH = getattr(settings, "SMSCOIN_VALIDATOR_PATH", "http://key.smscoin.com/key/")

SMSCOIN_TARIFF_PATH = SMSCOIN_TARIFF_BASE_PATH % settings.SMSCOIN_KEY
