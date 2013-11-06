#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2007-2012 Etienne Robillard <erob@gthcfoundation.org>
# All rights reserved.
# <LICENSE=ISC>
# XXX: deprecated don't use unless you know what you're doing. :-)
"""Django configuration settings for the BlogEngine app.

Usage: To use in a typical Django project, add the following line in your 
local_settings.py file:
::

    from blogengine.config.global_settings import *

Settings overview
-----------------

TODO

"""
BLOGENGINE = {}
BLOGENGINE['ENABLE_I18N'] = False
BLOGENGINE['DEBUG'] = True
BLOGENGINE['ITEMS_PER_PAGE'] = 8
BLOGENGINE['PAGE_MAX'] = 1
# Our set of generic views. 
BLOGENGINE['VIEWS'] = {'cleanlayout.index' : 'blogengine/frontpage.mako'}
BLOGENGINE['ADDTHIS_USERNAME'] = 'erob'
