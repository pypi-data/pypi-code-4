from Products.CMFCore.utils import getToolByName


DEPENDENCIES = (
    'raptus.article.additionalwysiwyg',
)


def installDependencies(context):
    """ Installs optional dependencies
    """
    if context.readDataFile('raptus.article.teaseme_install.txt') is None:
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
