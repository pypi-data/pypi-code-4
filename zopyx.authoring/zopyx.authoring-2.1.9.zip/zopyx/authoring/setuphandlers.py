#####################################################################
# zopyx.authoring
# (C) 2010, ZOPYX Limited, D-72070 Tuebingen. All rights reserved
#####################################################################

import config
from cStringIO import StringIO
from Products.CMFCore.utils import getToolByName

def importVarious(context):
    """
    Import various settings.

    Provisional handler that does initialization that is not yet taken
    care of by other handlers.
    """

    if context.readDataFile('zopyx-authoring.txt') is None:
        return
    site = context.getSite()
    logger = context.getLogger('zopyx.authoring')
    out = StringIO()
    installProducts(site)
    installMisc(site)
    logger.info(out.getvalue())


def installProducts(site):
    """QuickInstaller install of required Products"""

    qi = getToolByName(site, 'portal_quickinstaller')
    for product in config.DEPENDENCIES:
        if qi.isProductInstalled(product):
            qi.reinstallProducts([product])
        else:
            qi.installProduct(product, locked=0)


def installMisc(site):
    """ Misc """

    # Multiselect code must be moved to the end of the resource
    # registry since its loading depends on the availability of over jquery
    # modules
    js = getToolByName(site, 'portal_javascripts')

