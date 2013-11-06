#!/usr/bin/env python
# Copyright (C) 2007-2012 Etienne Robillard <erob@gthcfoundation.org>
# All rights reserved
# <LICENSE=ISC>
"""Basic logging utilities"""
import logging

__all__ = ['configure_logging']

def configure_logging(logger, level=40, loggingClass=logging.FileHandler):
    #XXX: use DJANGO_DEBUG_FILENAME here
    
    from notmm.utils.django_settings import SettingsProxy
    settings = SettingsProxy(autoload=True).get_settings()
    hdl = loggingClass(
        getattr(settings, 'DEBUG_FILENAME', '/var/log/django.log')
        )
    logger.addHandler(hdl)
    logger.setLevel(level)
    
    return logger

