from Products.CMFCore.utils import getToolByName

# Properties are defined here, because if they are defined in propertiestool.xml,
# all properties are re-set the their initial state if you reinstall product
# in the quickinstaller.


def import_various(context):
    if context.readDataFile('mybookmarksportlet-various.txt') is None:
        return
    # Define portal properties
    portal = context.getSite()
    insertProperties(context, portal)


def insertProperties(context, portal):
    """
    insert some properties
    """
    portal_properties = getToolByName(context, 'portal_properties')
    mybookmarks_properties = getattr(portal_properties, 'mybookmarks_properties', None)
    if not mybookmarks_properties:
        portal_properties.addPropertySheet(id='mybookmarks_properties', title="MyBookmarks properties")
        portal.plone_log("Added mybookmarks_properties property-sheet")
        mybookmarks_properties = getattr(portal_properties, 'mybookmarks_properties', None)
    if not mybookmarks_properties.hasProperty('default_bookmarks'):
        mybookmarks_properties.manage_addProperty(id='default_bookmarks', value='', type='lines')
        portal.plone_log("Added default_bookmarks property")
