"""Common configuration constants
"""
from AccessControl import ModuleSecurityInfo
from Products.CMFCore.permissions import setDefaultRoles

PROJECTNAME = 'raptus.article.table'

security = ModuleSecurityInfo('raptus.article.table.config')

security.declarePublic('ADD_PERMISSION')
ADD_PERMISSION = {}

ADD_PERMISSION['Table'] = 'raptus.article: Add Table'
setDefaultRoles(ADD_PERMISSION['Table'], ('Manager','Contributor',))

ADD_PERMISSION['Row'] = 'raptus.article: Add Row'
setDefaultRoles(ADD_PERMISSION['Row'], ('Manager','Contributor',))

security.declarePublic('OVERRIDE_DEFINITION')
OVERRIDE_DEFINITION = 'raptus.article: Override Table Definition'
setDefaultRoles(OVERRIDE_DEFINITION, ('Manager',))

security.declarePublic('MANAGE_DEFINITIONS')
MANAGE_DEFINITIONS = 'raptus.article: Manage Table Definitions'
setDefaultRoles(MANAGE_DEFINITIONS, ('Manager',))
