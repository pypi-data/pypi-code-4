# -*- coding: utf-8 -*-

from zope import interface
from zope.annotation.interfaces import IAnnotations
from redturtle.custommenu.factories.interfaces import ICustomMenuEnabled
from redturtle.custommenu.factories.config import ANN_CUSTOMMENU_KEY

def install(portal):
    setup_tool = portal.portal_setup
    setup_tool.setBaselineContext('profile-redturtle.custommenu.factories:default')
    setup_tool.runAllImportStepsFromProfile('profile-redturtle.custommenu.factories:default')

def uninstall(portal, reinstall=False):
    setup_tool = portal.portal_setup
    setup_tool.setBaselineContext('profile-redturtle.custommenu.factories:uninstall')
    setup_tool.runAllImportStepsFromProfile('profile-redturtle.custommenu.factories:uninstall')
    
    if not reinstall:
        cleanMenuCustomizations(portal)

def cleanMenuCustomizations(portal):
    """Remove all customization from the Plone site"""
    catalog = portal.portal_catalog
    results = catalog(object_provides=ICustomMenuEnabled.__identifier__)
    for x in results:
        obj = x.getObject()
        interface.noLongerProvides(obj, ICustomMenuEnabled)
        annotations = IAnnotations(obj)
        del annotations[ANN_CUSTOMMENU_KEY]
        print 'Removing customization of the "Add new..." menu at %s' % x.getPath()
        obj.reindexObject(['object_provides'])
    # Also the Plone site can be customized... check manually as it isn't in the catalog
    if ICustomMenuEnabled.providedBy(portal):
        interface.noLongerProvides(portal, ICustomMenuEnabled)
        annotations = IAnnotations(portal)
        del annotations[ANN_CUSTOMMENU_KEY]
        print 'Removing customization of the "Add new..." menu in the Plone site'
        