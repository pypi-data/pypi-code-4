#####################################################################
# zopyx.authoring
# (C) 2010, ZOPYX Limited, D-72070 Tuebingen. All rights reserved
#####################################################################

"""Definition of the AuthoringProject content type
"""

import os
import pkg_resources
from zope.interface import implements, directlyProvides

from Products.Archetypes import atapi
from Products.ATContentTypes.content import folder
from Products.ATContentTypes.content import schemata

from zopyx.authoring import authoringMessageFactory as _
from zopyx.authoring.interfaces import IAuthoringProject
from zopyx.authoring.config import PROJECTNAME

from .. import config

AuthoringProjectSchema = folder.ATFolderSchema.copy() + atapi.Schema((


    # -*- Your Archetypes field definitions here ... -*-
))

# Set storage on fields copied from ATFolderSchema, making sure
# they work well with the python bridge properties.

AuthoringProjectSchema['title'].storage = atapi.AnnotationStorage()
AuthoringProjectSchema['description'].storage = atapi.AnnotationStorage()

schemata.finalizeATCTSchema(
    AuthoringProjectSchema,
    folderish=True,
    moveDiscussion=False
)

package_home = os.path.dirname(__file__)

class AuthoringProject(folder.ATFolder):
    """Authoring Project"""
    implements(IAuthoringProject)

    meta_type = "AuthoringProject"
    schema = AuthoringProjectSchema

    title = atapi.ATFieldProperty('title')
    description = atapi.ATFieldProperty('description')

    # -*- Your ATSchema to Python Property Bridges Here ... -*-

    def getAuthoringProject(self):
        """ Acquisition trickery """
        return self

atapi.registerType(AuthoringProject, PROJECTNAME)
