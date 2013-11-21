"""Common configuration constants
"""
from AccessControl import ModuleSecurityInfo
from Products.CMFCore.permissions import setDefaultRoles

PROJECTNAME = 'raptus.article.maps'

security = ModuleSecurityInfo('raptus.article.maps.config')

security.declarePublic('ADD_PERMISSION')
ADD_PERMISSION = {}

ADD_PERMISSION['Map'] = 'raptus.article: Add Map'
setDefaultRoles(ADD_PERMISSION['Map'], ('Manager','Contributor',))

ADD_PERMISSION['Marker'] = 'raptus.article: Add Marker'
setDefaultRoles(ADD_PERMISSION['Marker'], ('Manager','Contributor',))
