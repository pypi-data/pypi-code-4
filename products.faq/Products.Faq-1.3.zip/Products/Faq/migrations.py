from Products.CMFCore.utils import getToolByName
try:
    from plone.app.folder.migration import BTreeMigrationView
    HAS_FOLDER = True
except ImportError:
    HAS_FOLDER = False


def upgrade_1000_to_1001(context):
    if not HAS_FOLDER:
        return

    portal = getToolByName(context, 'portal_url').getPortalObject()
    catalog = getToolByName(portal, 'portal_catalog')

    request = portal.REQUEST

    view = BTreeMigrationView(portal, request)
    for brain in catalog(portal_type='FaqFolder'):
        obj = brain.getObject()
        view.migrate(obj)


def upgrade_1000_to_1002(context):
    context.runImportStepFromProfile("profile-Products.Faq:default", 'rolemap')
