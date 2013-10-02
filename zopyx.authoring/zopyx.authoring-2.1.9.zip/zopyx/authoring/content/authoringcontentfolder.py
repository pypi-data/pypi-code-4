#####################################################################
# zopyx.authoring
# (C) 2010, ZOPYX Limited, D-72070 Tuebingen. All rights reserved
#####################################################################

"""Definition of the AuthoringContentFolder content type
"""

from zope.interface import implements, directlyProvides

from Products.Archetypes import atapi
from Products.ATContentTypes.content import folder
from Products.ATContentTypes.content import schemata

from zopyx.authoring import authoringMessageFactory as _
from zopyx.authoring.interfaces import IAuthoringContentFolder
from zopyx.authoring.config import PROJECTNAME

AuthoringContentFolderSchema = folder.ATFolderSchema.copy() + atapi.Schema((

    # -*- Your Archetypes field definitions here ... -*-

))

# Set storage on fields copied from ATFolderSchema, making sure
# they work well with the python bridge properties.

AuthoringContentFolderSchema['title'].storage = atapi.AnnotationStorage()
AuthoringContentFolderSchema['description'].storage = atapi.AnnotationStorage()

schemata.finalizeATCTSchema(
    AuthoringContentFolderSchema,
    folderish=True,
    moveDiscussion=False
)

class AuthoringContentFolder(folder.ATFolder):
    """Authoring Content Folder"""
    implements(IAuthoringContentFolder)

    meta_type = "AuthoringContentFolder"
    schema = AuthoringContentFolderSchema

    title = atapi.ATFieldProperty('title')
    description = atapi.ATFieldProperty('description')
    
    # -*- Your ATSchema to Python Property Bridges Here ... -*-

    def getContentFolder(self):
        """ return self """
        return self

atapi.registerType(AuthoringContentFolder, PROJECTNAME)
