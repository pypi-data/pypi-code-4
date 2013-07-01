"""Common configuration constants
"""

from AccessControl import ModuleSecurityInfo
from Products.CMFCore.permissions import setDefaultRoles

PROJECTNAME = 'raptus.header'

security = ModuleSecurityInfo('raptus.header.config')

security.declarePublic('ADD_PERMISSION')
ADD_PERMISSION = {}

ADD_PERMISSION['Header'] = 'raptus.header: Add Header'
setDefaultRoles(ADD_PERMISSION['Header'], ('Manager','Contributor',))