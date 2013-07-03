"""Common configuration constants
"""
from AccessControl import ModuleSecurityInfo
from Products.CMFCore.permissions import setDefaultRoles

PROJECTNAME = 'raptus.article.media'

security = ModuleSecurityInfo('raptus.article.media.config')

security.declarePublic('ADD_PERMISSION')
ADD_PERMISSION = {}
ADD_PERMISSION['Video'] = 'raptus.article: Add Video'
setDefaultRoles(ADD_PERMISSION['Video'], ('Manager','Contributor',))

ADD_PERMISSION['VideoEmbed'] = 'raptus.article: Add Embeded Video'
setDefaultRoles(ADD_PERMISSION['VideoEmbed'], ('Manager','Contributor',))

ADD_PERMISSION['Audio'] = 'raptus.article: Add Audio'
setDefaultRoles(ADD_PERMISSION['Audio'], ('Manager','Contributor',))
