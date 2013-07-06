#####################################################################
# zopyx.authoring
# (C) 2010, ZOPYX Limited, D-72070 Tuebingen. All rights reserved
#####################################################################

"""Definition of the AuthoringContentsFolder content type
"""

from zope.interface import implements, directlyProvides

from Products.Archetypes import atapi
from Products.ATContentTypes.content import folder
from Products.ATContentTypes.content import schemata

from zopyx.authoring import authoringMessageFactory as _
from zopyx.authoring.interfaces import IAuthoringContentsFolder
from zopyx.authoring.config import PROJECTNAME

AuthoringContentsFolderSchema = folder.ATFolderSchema.copy() + atapi.Schema((

    # -*- Your Archetypes field definitions here ... -*-

))

# Set storage on fields copied from ATFolderSchema, making sure
# they work well with the python bridge properties.

AuthoringContentsFolderSchema['title'].storage = atapi.AnnotationStorage()
AuthoringContentsFolderSchema['description'].storage = atapi.AnnotationStorage()

schemata.finalizeATCTSchema(
    AuthoringContentsFolderSchema,
    folderish=True,
    moveDiscussion=False
)

class AuthoringContentsFolder(folder.ATFolder):
    """Authoring Contents Folder"""
    implements(IAuthoringContentsFolder)

    meta_type = "AuthoringContentsFolder"
    schema = AuthoringContentsFolderSchema

    title = atapi.ATFieldProperty('title')
    description = atapi.ATFieldProperty('description')
    
    # -*- Your ATSchema to Python Property Bridges Here ... -*-

atapi.registerType(AuthoringContentsFolder, PROJECTNAME)
