#####################################################################
# zopyx.authoring
# (C) 2010, ZOPYX Limited, D-72070 Tuebingen. All rights reserved
#####################################################################

"""Definition of the AuthoringContentPage content type
"""

from zope.interface import implements

from Products.Archetypes import atapi
from Products.ATContentTypes.content import base
from Products.ATContentTypes.content import schemata

from zopyx.authoring import authoringMessageFactory as _
from zopyx.authoring.interfaces import IAuthoringContentPage
from zopyx.authoring.config import PROJECTNAME

from Products.ATContentTypes.content.document import ATDocument
from Products.ATContentTypes.interface.document import IATDocument


AuthoringContentPageSchema = ATDocument.schema.copy() + atapi.Schema((

    # -*- Your Archetypes field definitions here ... -*-

   atapi.TextField('footnotes',
                   label='Footnotes',
                   ),

   atapi.TextField('officeStyles',
                   widget=atapi.TextAreaWidget(rows=10, cols=60)
       ),
))

# Set storage on fields copied from ATContentTypeSchema, making sure
# they work well with the python bridge properties.

AuthoringContentPageSchema['title'].storage = atapi.AnnotationStorage()
AuthoringContentPageSchema['description'].storage = atapi.AnnotationStorage()

schemata.finalizeATCTSchema(AuthoringContentPageSchema, moveDiscussion=False)


class AuthoringContentPage(ATDocument):
    """Authoring Content Page"""
    implements(IAuthoringContentPage, IATDocument)

    meta_type = "AuthoringContentPage"
    schema = AuthoringContentPageSchema

    title = atapi.ATFieldProperty('title')
    description = atapi.ATFieldProperty('description')

    # -*- Your ATSchema to Python Property Bridges Here ... -*-

atapi.registerType(AuthoringContentPage, PROJECTNAME)
