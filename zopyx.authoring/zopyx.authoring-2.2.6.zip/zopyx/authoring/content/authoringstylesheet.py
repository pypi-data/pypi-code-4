"""Definition of the AuthoringStylesheet content type
"""

from zope.interface import implements, directlyProvides

from Products.Archetypes import atapi
from Products.ATContentTypes.content import base
from Products.ATContentTypes.content import schemata

from zopyx.authoring import authoringMessageFactory as _
from zopyx.authoring.interfaces import IAuthoringStylesheet
from zopyx.authoring.config import PROJECTNAME

from pretextareawidget import PreTextAreaWidget

from util import invisibleFields

AuthoringStylesheetSchema = schemata.ATContentTypeSchema.copy() + atapi.Schema((
atapi.TextField('stylesheet',
                  widget=PreTextAreaWidget(rows=20,
                                           cols=80,
                                           label=_('label_stylesheet',default='Stylesheet'),
                                          )
                  ),
atapi.FileField('upload',
                label='Upload',
                widget=atapi.FileWidget(visible=dict(edit='visible', view='invisible')), 
                ),

    # -*- Your Archetypes field definitions here ... -*-

))

# Set storage on fields copied from ATContentTypeSchema, making sure
# they work well with the python bridge properties.

AuthoringStylesheetSchema['title'].storage = atapi.AnnotationStorage()
AuthoringStylesheetSchema['description'].storage = atapi.AnnotationStorage()
invisibleFields(AuthoringStylesheetSchema, 
                'description',
                'allowDiscussion', 'relatedItems', 
                'excludeFromNav', 'subject', 'location', 
                'creators', 'contributors', 'rights',
                'language', 'effectiveDate', 'expirationDate')

schemata.finalizeATCTSchema(AuthoringStylesheetSchema, moveDiscussion=False)

class AuthoringStylesheet(base.ATCTContent):
    """Authoring Stylesheet"""
    implements(IAuthoringStylesheet)

    meta_type = "AuthoringStylesheet"
    schema = AuthoringStylesheetSchema

    title = atapi.ATFieldProperty('title')
    description = atapi.ATFieldProperty('description')


    def at_post_edit_script(self, *args, **kw):
        form_data = self.REQUEST.form
        if 'upload_file' in form_data:
            form_data['upload_file'].seek(0)
            css = form_data['upload_file'].read()
            if css:
                self.setStylesheet(css)
                self.setUpload(None)

    at_post_create_script = at_post_edit_script

    def update_data(self, data):
        """ update data """
        self.setStylesheet(data)       

    def get_data(self):
        """ return data """
        return self.getStylesheet()

    # -*- Your ATSchema to Python Property Bridges Here ... -*-

atapi.registerType(AuthoringStylesheet, PROJECTNAME)
