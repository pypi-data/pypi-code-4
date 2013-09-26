from Products.CMFCore.utils import getToolByName

from Products.projectmanager import logger


def reindex_actions(context):
    catalog = getToolByName(context, 'portal_catalog')
    actions = catalog.searchResults(portal_type='PM_Action')
    for action in actions:
        try:
            action_obj = action.getObject()
        except AttributeError:
            logger.error("%s action invalid", action.getPath())
            continue

        action_obj.reindexObject(idxs=['start', 'end'])

def add_hr_column(context):
    catalog = getToolByName(context, 'portal_catalog')
    if 'getHumanResources' not in catalog.schema():
        catalog.addColumn('getHumanResources')

    actions = catalog.searchResults(portal_type='PM_Action')
    for action in actions:
        try:
            action_obj = action.getObject()
        except AttributeError:
            logger.error("%s action invalid", action.getPath())
            continue

        action_obj.reindexObject(idxs=[])
