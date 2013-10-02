#####################################################################
# zopyx.authoring
# (C) 2011, ZOPYX Limited, D-72070 Tuebingen. All rights reserved
#####################################################################

"""Definition of the AuthoringConversionsCollection content type
"""

from zope.interface import implements

from Products.Archetypes import atapi
from Products.ATContentTypes.content import folder
from Products.ATContentTypes.content import schemata

# -*- Message Factory Imported Here -*-

from zopyx.authoring.interfaces import IAuthoringConversionsCollection
from zopyx.authoring.config import PROJECTNAME

AuthoringConversionsCollectionSchema = folder.ATFolderSchema.copy() + atapi.Schema((

    # -*- Your Archetypes field definitions here ... -*-

))

# Set storage on fields copied from ATFolderSchema, making sure
# they work well with the python bridge properties.

AuthoringConversionsCollectionSchema['title'].storage = atapi.AnnotationStorage()
AuthoringConversionsCollectionSchema['description'].storage = atapi.AnnotationStorage()

schemata.finalizeATCTSchema(
    AuthoringConversionsCollectionSchema,
    folderish=True,
    moveDiscussion=False
)


class AuthoringConversionsCollection(folder.ATFolder):
    """Collection for conversion folders"""
    implements(IAuthoringConversionsCollection)

    meta_type = "AuthoringConversionsCollection"
    schema = AuthoringConversionsCollectionSchema

    title = atapi.ATFieldProperty('title')
    description = atapi.ATFieldProperty('description')

    # -*- Your ATSchema to Python Property Bridges Here ... -*-

atapi.registerType(AuthoringConversionsCollection, PROJECTNAME)
