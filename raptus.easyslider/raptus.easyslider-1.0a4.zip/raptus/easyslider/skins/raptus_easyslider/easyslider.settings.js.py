## Script (Python) "easyslider.settings.js.py"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=foo=None,bar=None
##title=
##
from Products.CMFCore.utils import getToolByName

template = """easyslider = {
  settings : new Array(),
  count : 1
}
%(settings)s"""
settings_template = "easyslider.settings[\"%(id)s\"] = %(settings)s;"

properties = getToolByName(context, 'portal_properties').raptus_easyslider
settings = []
for id in properties.propertyIds():
    if not id == 'title':
        settings.append(settings_template % dict(id=id,
                                                 settings=properties.getProperty(id)))
return template % dict(settings="\n".join(settings))