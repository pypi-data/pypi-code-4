from zope import component
from zope.interface.interfaces import IInterface
from collective.flowplayer.interfaces import IFlowPlayerSite

from Products.CMFCore.utils import getToolByName

def install(context):
    """ Removes the persistent utility registered by collective.flowplayer
    """
    if context.readDataFile('raptus.article.media_install.txt') is None:
        return
    portal = context.getSite()
    manager = component.getSiteManager()
    
    util = manager.queryUtility(IInterface, name='collective.flowplayer.interfaces.IFlowPlayerSite')
    manager.unregisterUtility(util, IInterface, name='collective.flowplayer.interfaces.IFlowPlayerSite')
    del util
    try: # try deleting subscriber if available
        del manager.utilities._subscribers[0][IInterface]
    except:
        pass
    
    # install stxnext.transform.avi2flv if available
    inst = getToolByName(portal, 'portal_quickinstaller')
    prod = 'stxnext.transform.avi2flv'
    try:
        if not inst.isProductInstalled(prod):
            inst.installProduct(prod)
        else:
            inst.reinstallProducts(prod)
    except:
        pass
