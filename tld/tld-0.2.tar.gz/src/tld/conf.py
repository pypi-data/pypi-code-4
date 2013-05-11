#!/usr/bin/env python

# @package Tld
# @author Artur Barseghyan (artur.barseghyan@gmail.com)
# @version 0.1
# @license MPL 1.1/GPL 2.0/LGPL 2.1
# @link http://bitbucket.org/barseghyanartur/php-tld
#
# Tld conf

from django.conf import settings

from tld import defaults

def get_setting(setting, override=None):
    """
    Get a setting from tlds conf module, falling back to the default. If override is not None, it will be used instead
    of the setting.
    """
    if override is not None:
        return override
    if hasattr(settings, 'TLD_%s' % setting):
        return getattr(settings, 'TLD_%s' % setting)
    else:
        return getattr(defaults, setting)