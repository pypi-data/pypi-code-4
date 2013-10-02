#####################################################################
# zopyx.authoring
# (C) 2010, ZOPYX Limited, D-72070 Tuebingen. All rights reserved
#####################################################################

"""Definition of the AuthoringCoverPage content type
"""

from zope.interface import implements

from Products.Archetypes import atapi
from Products.ATContentTypes.content import base
from Products.ATContentTypes.content import schemata

from zopyx.authoring import authoringMessageFactory as _
from zopyx.authoring.interfaces import IAuthoringCoverPage
from zopyx.authoring.config import PROJECTNAME

from pretextareawidget import PreTextAreaWidget
from util import invisibleFields

coverpage_description =  _('help_coverpage', """
Use Zope TALES for scripting the cover pages. The content folder
is exposed through options/content_root and the request can be accessed using options/request.
The top-level content folder can be used to manage additional metadata like authors, dates
or contributors. The metadata can be accessed through the related accessor methods on the content_root
e.g. "options/content_root/Creators".
""")

AuthoringCoverPageSchema = schemata.ATContentTypeSchema.copy() + atapi.Schema((

    # -*- Your Archetypes field definitions here ... -*-
atapi.StringField('html',
                  widget=PreTextAreaWidget(rows=20,
                                           cols=80,
                                           label=_('label_coverpage', 'Coverpage'),
                                           description=coverpage_description,
                                          ),
)))

# Set storage on fields copied from ATContentTypeSchema, making sure
# they work well with the python bridge properties.

AuthoringCoverPageSchema['title'].storage = atapi.AnnotationStorage()
AuthoringCoverPageSchema['description'].storage = atapi.AnnotationStorage()

schemata.finalizeATCTSchema(AuthoringCoverPageSchema, moveDiscussion=False)

invisibleFields(AuthoringCoverPageSchema, 
                'description',
                'allowDiscussion', 'relatedItems', 
                'excludeFromNav', 'subject', 'location', 
                'creators', 'contributors', 'rights',
                'language', 'effectiveDate', 'expirationDate')

class AuthoringCoverPage(base.ATCTContent):
    """Authoring Cover Page"""
    implements(IAuthoringCoverPage)

    meta_type = "AuthoringCoverPage"
    schema = AuthoringCoverPageSchema

    title = atapi.ATFieldProperty('title')
    description = atapi.ATFieldProperty('description')

    # -*- Your ATSchema to Python Property Bridges Here ... -*-

    def get_data(self):
        """ return data """
        return self.getHtml()

    def update_data(self, data):
        """ set data """
        try:
            self.setHtml(data.read())
        except AttributeError: 
            self.setHtml(data)       

atapi.registerType(AuthoringCoverPage, PROJECTNAME)
