#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-
__author__ = 'yarnaid'

import logging
try:
    import colorer
except:
    import glespy.tools.colorer


logging.basicConfig(
    format='[%(funcName)s][%(asctime)s] %(levelname)s: %(message)s')
logging.basicConfig(datefmt='%m/%d/%Y %I:%M:%S %p')
logging.basicConfig(level=logging.INFO)
logging.basicConfig(levelname=logging.INFO)


logger = logging.getLogger()
logger.INFO = logging.INFO
logger.DEBUG = logging.DEBUG
logger.CRITICAL = logging.CRITICAL
logger.WARNING = logging.WARNING
logger.ERROR = logging.ERROR
logger.NOTSET = logging.NOTSET
logger.setLevel(logger.INFO)
logger.setLevel(logger.DEBUG)
# logger.setLevel(logger.CRITICAL)
