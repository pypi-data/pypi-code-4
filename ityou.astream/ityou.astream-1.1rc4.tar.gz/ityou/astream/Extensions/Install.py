import logging
from StringIO import StringIO
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

def remove_layout_properties(self):
    """Removes the layout properties of the project
    """
    portal = getSite()
    activities_layout = "activities"
    
    catalog = getToolByName(portal,'portal_catalog')
    folders = catalog(portal_type='Folder')
    for f in folders:
        folder = f.getObject()
        if folder.getLayout() == activities_layout:
            print "\t - Reset layout of %s" % f.getId 
            folder.setLayout('folder_listing')
    # Site root ------
    if portal.getLayout() == activities_layout:
        print "\t - Reset layout of root %s" % f.getId 
        portal.setLayout('folder_listing')
    
def uninstall(self):
    """We need to uninstall the views???"""
    out = StringIO()
    logging.info("Uninstalling ITYOU Activity stream" )
        
    remove_layout_properties(self)
    print >> out, "Successfully uninstalled ityou.astream"

    return out.getvalue()

    