# -*- coding: utf-8 -*-
import logging
logger = logging.getLogger('collective.rtvideo.mediacore')

from os import environ
timeout_value_str = environ.get('URLLIB_TIMEOUT', 'Missing value')

try:
    DEFAULT_TIMEOUT = int(timeout_value_str)
except ValueError:
    DEFAULT_TIMEOUT = 15
    msg = ('Unparsable URLLIB_TIMEOUT environment variable : %s. '
           'We use %ss as default timeout.'
           ) % (timeout_value_str, DEFAULT_TIMEOUT)
    logger.warning(msg)
