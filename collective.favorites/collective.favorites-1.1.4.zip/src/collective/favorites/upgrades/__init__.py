from Products.CMFCore.utils import getToolByName
def v1(context):
    js_registry = getToolByName(context, 'portal_javascripts')
    js_registry.cookResources()