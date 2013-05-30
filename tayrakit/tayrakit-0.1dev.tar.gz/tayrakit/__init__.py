# -*- coding: utf-8 -*-

# This file is subject to the terms and conditions defined in
# file 'LICENSE', which is part of this source code package.
#       Copyright (c) 2011 R Pratap Chakravarthy

from tayra import loadttls

__version__ = '0.1dev'

template_plugins = [
    'tayrakit:plugins/tbreadcrumbs.ttl',
    'tayrakit:plugins/pluggdapps_footer.ttl'
]

def package( pa ) :
    """A pluggdapps package must implement this entry point. This function
    will be called during platform pre-booting. Other than some initialization
    stuff, like dynamically loading template plugins using :func:`loadttls`,
    this entry point must return a dictionary of key,value pairs describing
    the package.
    """
    loadttls( pa, template_plugins )
    return {
        'ttlplugins' : template_plugins,
    }
