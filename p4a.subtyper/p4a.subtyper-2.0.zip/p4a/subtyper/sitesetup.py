from p4a.common import site
from p4a.z2utils import utils
from Products.CMFCore.utils import getToolByName
from Products.CMFCore import utils as cmfutils
from Products.CMFCore import DirectoryView
from p4a.subtyper import interfaces
from zope.interface import Interface
from plone.app.contentmenu.interfaces import IContentMenuItem
    
import logging
logger = logging.getLogger('p4a.subtyper.sitesetup')

try:
    import five.localsitemanager
    HAS_FLSM = True
    logger.info('Using five.localsitemanager')
except ImportError, err:
    HAS_FLSM = False


# Unused:
def setup_portal(portal):
    site.ensure_site(portal)
    setup_site(portal)


# Unused:
def setup_site(site):
    # In 2.5, install the subtyper profile:
    mt = cmfutils.getToolByName(site, 'portal_migration')
    plone_version = mt.getInstanceVersion()

    # Register profile for Plone 3.
    if int(plone_version[0]) >= 3:
        quickinstaller_tool = getToolByName(site, 'portal_quickinstaller')
        quickinstaller_tool.installProduct('p4a.subtyper')

    if plone_version[0:3] == '2.5':
        # Setup only needed for Plone 3.0
        skin_tool = cmfutils.getToolByName(site, 'portal_skins')
        path = None
        for path in DirectoryView.manage_listAvailableDirectories():
            if path.endswith('p4a_subtyper'):
                break
        assert(path is None, "Subtyper skin directory not found")
        if 'p4a_subtyper' not in skin_tool.objectIds():
            DirectoryView.createDirectoryView(skin_tool, path)

        for skin_name, paths in skin_tool.getSkinPaths():
            if not 'p4a_subtyper' in paths:
                paths = paths.split(',')
                index = paths.index('plone_templates')
                paths.insert(index, 'p4a_subtyper')
                paths = ','.join(paths)
                skin_tool._getSelections()[skin_name] = paths

# Used:
def unsetup_portal(portal, reinstall=False, reindex=True):
    if reinstall:
        # Do nothing.
        return
    if reindex:
        # Setting marker interfaces doesn't reindex objects, so we need to
        # reindex object_provides to make sure it's up to date. If called
        # from other products that already have done this pass reindex=False.
        portal.portal_catalog.manage_reindexIndex(('object_provides', ))
    # Then we can use the removal utility to unregister all of them:
    count = utils.remove_marker_ifaces(portal, interfaces.ISubtyped)
    logger.warn('Removed ISubtyped interface from %i objects for '
                'cleanup' % count)

    sm = portal.getSiteManager()
    if sm.adapters.lookup((Interface, Interface), IContentMenuItem, u'subtypes') is not None:
        sm.unregisterAdapter(None, (Interface, Interface), IContentMenuItem, u'subtypes')

