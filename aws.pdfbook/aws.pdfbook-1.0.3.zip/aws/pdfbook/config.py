# -*- coding: utf-8 -*-
# $Id: config.py 117058 2010-05-07 12:11:07Z glenfant $
"""Global configuration data"""

PROJECTNAME = 'aws.pdfbook'
GLOBALS = globals()
PROPERTYSHEET = 'aws_pdfbook_properties'

# Configuration data from zope.conf

SITE_CHARSET = None
DOWNLOAD_BUFFER_SIZE = None

def readZopeConf():
    """Overriding default values with the ones from zope.conf
    """
    global SITE_CHARSET, DOWNLOAD_BUFFER_SIZE

    if SITE_CHARSET is not None:
        # We run this only once
        return

    default_pdfbook_config = {
        'site-charset': 'utf-8',
        'download-buffer-size': '40000'
        }

    from App.config import getConfiguration
    try:
        pdfbook_config = getConfiguration().product_config[PROJECTNAME.lower()]
    except (KeyError, AttributeError):
        # Zope 2.10 raises a KeyError when Zope 2.12 raises an AttributeError
        # if the <product-config ...> is missing in zope.conf
        pdfbook_config =  default_pdfbook_config
    getConfData = lambda key: pdfbook_config.get(key, default_pdfbook_config[key])
    SITE_CHARSET = getConfData('site-charset')
    DOWNLOAD_BUFFER_SIZE = int(getConfData('download-buffer-size'))
    return

readZopeConf()
del readZopeConf
