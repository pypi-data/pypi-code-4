import logging

from zope.component import getMultiAdapter, getUtility
from zope.container.interfaces import INameChooser

from plone.portlets.interfaces import IPortletManager
from plone.portlets.interfaces import IPortletAssignmentMapping

from Products.CMFCore.utils import getToolByName

from collective.blogging.interfaces import IEntryMarker, IBlogMarker    

from collective.blogging.interfaces import IBlog
from collective.blogging.portlets import filter

logger = logging.getLogger("collective.blogging")
PROFILE_ID = 'profile-collective.blogging:default'


def reindexPublishDates(context):
    logger.info("Starting reindex existing blog entries.")
    catalog = getToolByName(context, 'portal_catalog')
    entry_brains = catalog(
        object_provides=IEntryMarker.__identifier__,
        Language=u'all'
    )
    logger.info("Found %s blog enries with old publishing indexes.", len(entry_brains))
    for brain in entry_brains:
        try:
            entry = brain.getObject()
        except (AttributeError, KeyError):
            logger.warn("AttributeError getting entry object at %s",
                        brain.getURL())
            continue
        
        entry.reindexObject()
        logger.info('Entry "%s" reindexed.' % brain.getPath())


def migrateLayouts(context):
    logger.info("Starting blogging layouts migration.")
    catalog = getToolByName(context, 'portal_catalog')
    blog_brains = catalog(
        object_provides=IBlogMarker.__identifier__,
        Language=u'all'
    )
    
    logger.info("Found %s blogs...", len(blog_brains))
    for brain in blog_brains:
        brain.getObject().setLayout('blog-view')
        logger.info('Layout migrated for blog: "%s".' % brain.getPath())
    
    
    
    catalog = getToolByName(context, 'portal_catalog')
    entry_brains = catalog(
        object_provides=IEntryMarker.__identifier__,
        Language=u'all'
    )
    
    logger.info("Found %s entries...", len(entry_brains))
    for brain in entry_brains:
        brain.getObject().setLayout('entry-view')
        logger.info('Layout migrated for entry: "%s".' % brain.getPath())

    logger.info("Blogging layouts migration completed.")

def removeGalleryView(context):
    logger.info("Removing blog gallery view.")
    
    catalog = getToolByName(context, 'portal_catalog')
    content = catalog(portal_type=['Folder', 'Large Plone Folder', 'Topic'])
    for brain in content:
        obj = brain.getObject()
        if obj.getLayout() == 'blog-gallery':
            obj.setLayout('atct_album_view')
            logger.info('Default "%s" layout set for "%s".' % ('atct_album_view', brain.getPath()))
    
    
    portal_types = getToolByName(context, 'portal_types')
    for ptype in ['Folder', 'Large Plone Folder', 'Topic']:
        type_info = portal_types.getTypeInfo(ptype)
        if 'blog-gallery' in type_info.view_methods:
            type_info.view_methods = tuple([vm for vm in type_info.view_methods if vm !='blog-gallery'])
            logger.info('"%s" view uninstalled for %s.' % ('blog-gallery', ptype))
    
    logger.info("Gallery view removed.")

def setFilterPortlet(context):
    logger.info("Replacing filter toolbars with filter portlets.")
    catalog = getToolByName(context, 'portal_catalog')
    brains = catalog(object_provides=IBlog.__identifier__, blogged=True)
    for brain in brains:
        blog = brain.getObject()
        blog_path = '/' + ('/'.join(blog.getPhysicalPath()[2:]))
        logger.info('Upgrading blog at %s' % (blog_path))
        settings = {'enable_toolbar': {'value': None, 'default': 'Empty'}, 'filter_cache': {'value': None, 'default': 60}, 'enable_count': {'value': None, 'default': False}}
        for field_name in settings:
            default = settings[field_name]['default']
            settings[field_name]['value'] = getattr(blog, field_name, default)
            if hasattr(blog, field_name):
                delattr(blog, field_name)
        
        toolbar = settings['enable_toolbar']['value']
        if toolbar!='Empty' and toolbar:
            column = getUtility(IPortletManager, name=u'plone.rightcolumn')
            manager = getMultiAdapter((blog, column,), IPortletAssignmentMapping)
            assignment = filter.Assignment(target_blog=blog_path, filter_cache=settings['filter_cache']['value'], enable_count=settings['enable_count']['value'])
            chooser = INameChooser(manager)
            manager[chooser.chooseName(None, assignment)] = assignment
            
    logger.info("Toolbars replaced")
