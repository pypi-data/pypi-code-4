from StringIO import StringIO
import logging
from plone.portlets.utils import unregisterPortletType
from zope.app.component.hooks import getSite
from zope.component import getSiteManager
from zope.component import getUtilitiesFor
from zope.component import adapts
from zope.component import queryMultiAdapter
from zope.component import queryUtility
from zope.component import getUtility
from zope.component import getMultiAdapter
from plone.portlets.interfaces import IPortletType
from plone.portlets.interfaces import IPortletManager
from plone.portlets.interfaces import IPortletManagerRenderer
from plone.portlets.interfaces import ILocalPortletAssignmentManager
from plone.portlets.interfaces import IPortletAssignmentMapping
from plone.portlets.interfaces import IPortletAssignmentSettings
from plone.portlets.interfaces import IPortletAssignment
from Products.CMFCore.utils import getToolByName

def remove_portlet_assignment(self):
    """Removes the portlet Assignment
    """
    content = getSite()
    for manager_name in [ "plone.leftcolumn", "plone.rightcolumn" ]:
        print "Checking: " + manager_name
        manager = getUtility(IPortletManager, name=manager_name, context=content)
        mapping = getMultiAdapter((content, manager), IPortletAssignmentMapping, context=content)
        for ap  in ['whoami','whoisonline']:
            if ap in mapping:
                logging.info( "\t Remove %s" % ap)
                del mapping[ap] 

    
def uninstall(self):
    """We need to uninstall the portlets GS???"""
    out = StringIO()
    logging.info("Uninstalling ITYOU WhoIsOnline" )
    remove_portlet_assignment(self)
    print >> out, "Successfully uninstalled ityou.whoisonline"

    return out.getvalue()

    
