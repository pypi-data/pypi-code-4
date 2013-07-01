from Products.CMFCore.utils import getToolByName


DEPENDENCIES = (
    'raptus.article.nesting',
    'raptus.article.media',
    'raptus.article.teaser',
)


def installDependencies(context):
    """ Installs optional dependencies
    """
    if context.readDataFile('raptus.article.mediagallery_install.txt') is None:
        return
    portal = context.getSite()

    inst = getToolByName(portal, 'portal_quickinstaller')
    for prod in DEPENDENCIES:
        try:
            if not inst.isProductInstalled(prod):
                inst.installProduct(prod)
            else:
                inst.reinstallProducts(prod)
        except:
            pass
