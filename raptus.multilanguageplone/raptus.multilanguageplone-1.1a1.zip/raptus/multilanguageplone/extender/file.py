from zope.component import adapts
from Products.Archetypes import PloneMessageFactory as _
from Products.validation import V_REQUIRED

from Products.Archetypes.atapi import AnnotationStorage
from Products.ATContentTypes.content.file import ATFile

from raptus.multilanguagefields import widgets
import fields

from base import DefaultExtender

title_field = [
        fields.StringField(
            name='title',
            required=False,
            searchable=True,
            default='',
            accessor='Title',
            widget=widgets.StringWidget(
                label_msgid='label_title',
                visible={'view' : 'invisible'},
                i18n_domain='plone',
            ),
        ),]

class FileExtender(DefaultExtender):
    adapts(ATFile)

    fields = DefaultExtender.fields + title_field + [
        fields.FileField('file',
            required=True,
# we got an error with this attribute on Plone 3.3
# Tried to add 'text___fr___' as primary field but <Products.Archetypes.Schema.Schema object at 0x0AE1BBD0> already has the primary field 'text'
#
# we need the primary marker here to have multilanguage files working
            primary=True,
            searchable=True,
            languageIndependent=False,
            storage = AnnotationStorage(migrate=True),
            widget = widgets.FileWidget(
                description = '',
                label=_(u'label_file', default=u'File'),
                show_content_type = False,
            )
        ),
    ]

try:
    from zope.interface import implements
    from plone.app.blob.interfaces import IATBlobFile
    from archetypes.schemaextender.interfaces import ISchemaModifier
    
    class BlobFileExtender(DefaultExtender):
        adapts(IATBlobFile)
    
        fields = DefaultExtender.fields + title_field

    class BlobFileModifier(object):
        adapts(IATBlobFile)
        implements(ISchemaModifier)
        
        field = fields.BlobFileField('file',
                    required = True,
                    primary = True,
                    searchable = True,
                    accessor = 'getFile',
                    mutator = 'setFile',
                    index_method = 'getIndexValue',
                    languageIndependent = True,
                    storage = AnnotationStorage(migrate=True),
                    validators = (('isNonEmptyFile', V_REQUIRED),
                                  ('checkFileMaxSize', V_REQUIRED)),
                    widget = widgets.FileWidget(
                        description = '',
                        label=_(u'label_file', default=u'File'),
                        show_content_type = False,
                    )
                )
        
        def __init__(self, context):
            self.context = context
            
        def fiddle(self, schema):
            schema['file'] = self.field
            return schema
except:
    pass
