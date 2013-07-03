## Script (Python) "lightbox.settings.js.py"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=foo=None,bar=None
##title=
##
from Products.CMFCore.utils import getToolByName

properties = getToolByName(context, 'portal_properties').site_properties
return """var lightbox_settings = %s;""" % properties.getProperty('jsImagePopups', '{}')