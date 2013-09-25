from Products.CMFCore.utils import getToolByName

# Properties are defined here, because if they are defined in propertiestool.xml,
# all properties are re-set the their initial state if you reinstall product
# in the quickinstaller.


_PROPERTIES = [ dict(name='header_allow_inheritance', type_='boolean', value=True),
                dict(name='header_width', type_='int', value=0),
                dict(name='header_height', type_='int', value=0),
                dict(name='header_responsive', type_='boolean', value=False)]

def setupProperties(context):
    if not context.readDataFile('raptus.header_setupProperties.txt'):
        return

    portal = context.getSite()

    props = getToolByName(portal, 'portal_properties').site_properties
    for prop in _PROPERTIES:
        if not props.hasProperty(prop['name']):
            props.manage_addProperty(prop['name'], prop['value'], prop['type_'])