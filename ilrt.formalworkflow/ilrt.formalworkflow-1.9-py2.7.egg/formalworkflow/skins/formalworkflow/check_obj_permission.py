## Python Script "check_obj_permission"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=permission
##title=Delete objects from a folder permission check
##
from Products.CMFCore.utils import getToolByName

mt = getToolByName(context, 'portal_membership')
if mt.checkPermission(permission, context):
    return True
return False

