#####################################################################
# zopyx.authoring
# (C) 2010, ZOPYX Limited, D-72070 Tuebingen. All rights reserved
#####################################################################

"""Definition of the AuthoringImageResource content type
"""

from zope.interface import implements, directlyProvides

from Products.Archetypes import atapi
from Products.ATContentTypes.content import base
from Products.ATContentTypes.content import schemata
from Products.ATContentTypes.content.image import ATImage, ATImageSchema
from Products.ATContentTypes.interface.image import IATImage

from zopyx.authoring import authoringMessageFactory as _
from zopyx.authoring.interfaces import IAuthoringImageResource
from zopyx.authoring.config import PROJECTNAME

from util import invisibleFields

AuthoringImageResourceSchema = ATImageSchema.copy() + atapi.Schema((

    # -*- Your Archetypes field definitions here ... -*-

))

# Set storage on fields copied from ATContentTypeSchema, making sure
# they work well with the python bridge properties.

AuthoringImageResourceSchema['title'].storage = atapi.AnnotationStorage()
AuthoringImageResourceSchema['description'].storage = atapi.AnnotationStorage()
invisibleFields(AuthoringImageResourceSchema, 
                 'allowDiscussion', 'relatedItems', 
                'excludeFromNav', 'subject', 'location', 
                'creators', 'contributors', 'rights',
                'language', 'effectiveDate', 'expirationDate')

schemata.finalizeATCTSchema(AuthoringImageResourceSchema, moveDiscussion=False)

class AuthoringImageResource(ATImage):
    """Authoring Image Resource"""
    implements(IAuthoringImageResource)

    meta_type = "AuthoringImageResource"
    schema = AuthoringImageResourceSchema
    default_view = immediate_view = 'image_view'

    def get_data(self):
        """ return data """
        return str(self.getImage().data)

atapi.registerType(AuthoringImageResource, PROJECTNAME)
