# -*- coding: utf-8 -*-

import logging

TEST_KEY = u'AKIAIUV632HFO2XMTROA'
TEST_SECRET = u'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'
TEST_BUCKET = u'opensource-test'

botoLogger = logging.getLogger('boto')
botoLogger.setLevel(logging.CRITICAL)