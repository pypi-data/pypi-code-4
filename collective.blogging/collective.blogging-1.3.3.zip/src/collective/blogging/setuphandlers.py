from logging import getLogger
from Products.CMFCore.utils import getToolByName
from plone.browserlayer import utils as layerutils
from collective.blogging.interfaces import IBloggingSpecific
from collective.blogging.interfaces import IEntryMarker, IBlogMarker

log = getLogger('collective.blogging')


INDEXES = {
    'publish_year' : 'FieldIndex',
    'publish_month': 'FieldIndex',
    'blogged'      : 'FieldIndex',
}

METADATA = [
    'publish_year',
    'publish_month',
    'total_comments',
]

BLOG_TYPES = ('Folder', 'Topic')
BLOG_VIEWS = ('blog-view',)

ENTRY_TYPES = ('Document', 'News Item', 'Event', 'File', 'Image', 'Link')
ENTRY_VIEWS = ('entry-view',)

def setupCatalog(context):

    if context.readDataFile('collective.blogging_various.txt') is None:
        return

    portal = context.getSite()
    catalog = getToolByName(portal, 'portal_catalog')

    idxs = catalog.indexes()
    mtds = catalog.schema()
    
    for index in INDEXES.keys():
        if index not in idxs:
            catalog.addIndex(index, INDEXES[index])
            log.info('Catalog index "%s" installed.' % index)
    
    for mt in METADATA:
        if mt not in mtds:
            catalog.addColumn(mt)
            log.info('Catalog metadata "%s" installed.' % mt)

    # re-index blog content if exists (useful when reinstalling)
    blogs = catalog(object_provides=IBlogMarker.__identifier__)
    for blog in blogs:
        obj = blog.getObject()
        obj.reindexObject(idxs=INDEXES.keys())
    log.info('Reindexed %d blogs.' % len(blogs))
    
    entries = catalog(object_provides=IEntryMarker.__identifier__)
    for entry in entries:
        obj = entry.getObject()
        obj.reindexObject(idxs=INDEXES.keys())
    log.info('Reindexed %d entries.' % len(entries))


def resetCatalog(context):

    if context.readDataFile('collective.blogging_uninstall.txt') is None:
        return

    portal = context.getSite()
    catalog = getToolByName(portal, 'portal_catalog')

    idxs = catalog.indexes()
    mtds = catalog.schema()
    
    for index in INDEXES.keys():
        if index in idxs:
            catalog.delIndex(index)
            log.info('Catalog index "%s" removed.' % index)
    
    for mt in METADATA:
        if mt in mtds:
            catalog.delColumn(mt)
            log.info('Catalog metadata "%s" removed.' % mt)

def setupViews(context):

    if context.readDataFile('collective.blogging_various.txt') is None:
        return

    portal = context.getSite()
    portal_types = getToolByName(portal, 'portal_types')

    for ptype in BLOG_TYPES:
        for view_method in BLOG_VIEWS:
            type_info = portal_types.getTypeInfo(ptype)
            if type_info and (type_info and view_method not in type_info.view_methods):
                type_info.view_methods = type_info.view_methods + (view_method,)
                log.info('"%s" view installed for %s.' % (view_method, ptype))

    for ptype in ENTRY_TYPES:
        for view_method in ENTRY_VIEWS:
            type_info = portal_types.getTypeInfo(ptype)
            if view_method not in type_info.view_methods:
                type_info.view_methods = type_info.view_methods + (view_method,)
                log.info('"%s" view installed for %s.' % (view_method, ptype))


def resetViews(context):

    if context.readDataFile('collective.blogging_uninstall.txt') is None:
        return

    portal = context.getSite()
    portal_types = getToolByName(portal, 'portal_types')

    for ptype in BLOG_TYPES:
        for view_method in BLOG_VIEWS:
            type_info = portal_types.getTypeInfo(ptype)
            if type_info and view_method in type_info.view_methods:
                type_info.view_methods = tuple([vm for vm in type_info.view_methods if vm !=view_method])
                log.info('"%s" view uninstalled for %s.' % (view_method, ptype))
    
    for ptype in ENTRY_TYPES:
        for view_method in ENTRY_VIEWS:
            type_info = portal_types.getTypeInfo(ptype)
            if view_method in type_info.view_methods:
                type_info.view_methods = tuple([vm for vm in type_info.view_methods if vm !=view_method])
                log.info('"%s" view uninstalled for %s.' % (view_method, ptype))


def resetLayers(context):
    if context.readDataFile('collective.blogging_uninstall.txt') is None:
        return
    
    if IBloggingSpecific in layerutils.registered_layers():
        layerutils.unregister_layer(name='collective.blogging')
        log.info('Browser layer "collective.blogging" uninstalled.')


def resetRoles(context):
    if context.readDataFile('collective.blogging_uninstall.txt') is None:
        return
    
    portal = context.getSite()
    portal._delRoles(['Blogger'])
    log.info('"Blogger" security role removed.')
