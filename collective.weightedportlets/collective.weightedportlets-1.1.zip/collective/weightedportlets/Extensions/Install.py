from zope.interface import Interface
from zope.component import getSiteManager
from plone.portlets.interfaces import IPortletManager, IPortletRetriever
from plone.app.portlets.exportimport.interfaces import IPortletAssignmentExportImportHandler


def uninstall(portal):
    sm = getSiteManager(context=portal)
    sm.unregisterAdapter(required=(Interface, IPortletManager), provided=IPortletRetriever)
    sm.unregisterAdapter(required=(Interface,), provided=IPortletAssignmentExportImportHandler)
