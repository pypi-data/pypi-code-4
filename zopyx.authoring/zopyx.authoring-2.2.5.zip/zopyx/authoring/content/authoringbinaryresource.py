#####################################################################
# zopyx.authoring
# (C) 2010, ZOPYX Limited, D-72070 Tuebingen. All rights reserved
#####################################################################

"""Definition of the AuthoringBinaryResource content type
"""

from zope.interface import implements, directlyProvides

from Products.Archetypes import atapi
from Products.ATContentTypes.content import base
from Products.ATContentTypes.content.file import ATFile, ATFileSchema
from Products.ATContentTypes.content import schemata

from zopyx.authoring import authoringMessageFactory as _
from zopyx.authoring.interfaces import IAuthoringBinaryResource
from zopyx.authoring.config import PROJECTNAME

from util import invisibleFields

AuthoringBinaryResourceSchema = ATFileSchema.copy() + atapi.Schema((

    # -*- Your Archetypes field definitions here ... -*-

))

# Set storage on fields copied from ATContentTypeSchema, making sure
# they work well with the python bridge properties.

AuthoringBinaryResourceSchema['title'].storage = atapi.AnnotationStorage()
AuthoringBinaryResourceSchema['description'].storage = atapi.AnnotationStorage()
invisibleFields(AuthoringBinaryResourceSchema, 
                 'allowDiscussion', 'relatedItems', 
                'excludeFromNav', 'subject', 'location', 
                'creators', 'contributors', 'rights',
                'language', 'effectiveDate', 'expirationDate')

schemata.finalizeATCTSchema(AuthoringBinaryResourceSchema, moveDiscussion=False)

class AuthoringBinaryResource(ATFile):
    """Authoring Binary Resource"""
    implements(IAuthoringBinaryResource)

    meta_type = "AuthoringBinaryResource"
    schema = AuthoringBinaryResourceSchema

    def get_data(self):
        """ return data """
        return str(self.getFile().data)

atapi.registerType(AuthoringBinaryResource, PROJECTNAME)
