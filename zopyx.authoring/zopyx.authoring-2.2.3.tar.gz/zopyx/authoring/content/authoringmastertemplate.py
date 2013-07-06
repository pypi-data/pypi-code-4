#####################################################################
# zopyx.authoring
# (C) 2010, ZOPYX Limited, D-72070 Tuebingen. All rights reserved
#####################################################################

"""Definition of the AuthoringMasterTemplate content type
"""

from zope.interface import implements, directlyProvides

from Products.Archetypes import atapi
from Products.ATContentTypes.content import base
from Products.ATContentTypes.content import schemata

from zopyx.authoring import authoringMessageFactory as _
from zopyx.authoring.interfaces import IAuthoringMasterTemplate
from zopyx.authoring.config import PROJECTNAME

from pretextareawidget import PreTextAreaWidget

from util import invisibleFields

html_description = _('help_master_template', """
The authoring theme defines all resources and defines the overall structure of the 
generated documents. Use Zope TALES for scripting the authoring theme. The content folder
is exposed through options/content_root and the request can be accessed using options/request.
The top-level content folder can be used to manage additional metadata like authors, dates
or contributors. The metadata can be accessed through the related accessor methods on the content_root
e.g. "options/content_root/Creators".
""")

AuthoringMasterTemplateSchema = schemata.ATContentTypeSchema.copy() + atapi.Schema((
atapi.StringField('html',
                  widget=PreTextAreaWidget(rows=20,
                                           label=_('label_master_template','HTML template'),
                                           description=html_description,
                                           cols=80,
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

AuthoringMasterTemplateSchema['title'].storage = atapi.AnnotationStorage()
AuthoringMasterTemplateSchema['description'].storage = atapi.AnnotationStorage()
invisibleFields(AuthoringMasterTemplateSchema, 
                'description',
                'allowDiscussion', 'relatedItems', 
                'excludeFromNav', 'subject', 'location', 
                'creators', 'contributors', 'rights',
                'language', 'effectiveDate', 'expirationDate')

schemata.finalizeATCTSchema(AuthoringMasterTemplateSchema, moveDiscussion=False)

class AuthoringMasterTemplate(base.ATCTContent):
    """Authoring Master Template"""
    implements(IAuthoringMasterTemplate)

    meta_type = "AuthoringMasterTemplate"
    schema = AuthoringMasterTemplateSchema

    title = atapi.ATFieldProperty('title')
    description = atapi.ATFieldProperty('description')
    
    def at_post_edit_script(self, *args, **kw):
        
        form_data = self.REQUEST.form
        if 'upload_file' in form_data:
            form_data['upload_file'].seek(0)
            html = form_data['upload_file'].read()
            if html:
                self.setHtml(html)
                self.setUpload(None)

    at_post_create_script = at_post_edit_script

    def update_data(self, data):
        """ update data """
        try:
            self.setHtml(data.read())
        except AttributeError: 
            self.setHtml(data)       


    def get_data(self):
        """ return data """
        return self.getHtml()
    # -*- Your ATSchema to Python Property Bridges Here ... -*-

atapi.registerType(AuthoringMasterTemplate, PROJECTNAME)
