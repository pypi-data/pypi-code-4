from Products.CMFCore.utils import getToolByName

def setupCatalog(context):
    # Only run step if a flag file is present (e.g. not an extension profile)
    if context.readDataFile('raptus.article.table-catalog.txt') is None:
        return

    site = context.getSite()
    
    catalog = getToolByName(site, 'portal_catalog')
    if not 'getDefinition' in catalog.indexes():
        catalog.addIndex('getDefinition', 'FieldIndex', None)
        catalog.reindexIndex('getDefinition')
