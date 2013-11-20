from zope.component import adapts
from Products.Archetypes import PloneMessageFactory as _

from Products.Archetypes.atapi import AnnotationStorage
from Products.ATContentTypes.configuration import zconf
from Products.ATContentTypes.content.document import ATDocument

from raptus.multilanguagefields import widgets
import fields

from base import DefaultExtender

class DocumentExtender(DefaultExtender):
    adapts(ATDocument)

    fields = DefaultExtender.fields + [
        fields.TextField('text',
                  required=False,
                  searchable=True,
# we got an error with this attribute on Plone 3.3
# Tried to add 'text___fr___' as primary field but <Products.Archetypes.Schema.Schema object at 0x0AE1BBD0> already has the primary field 'text'
#
# we need the primary markers to have the getContentType method working
                  primary=True,
                  storage = AnnotationStorage(migrate=True),
                  default_output_type = 'text/x-html-safe',
                  widget = widgets.RichWidget(
                            description = '',
                            label = _(u'label_body_text', default=u'Body Text'),
                            rows = 25,
                            allow_file_upload = zconf.ATDocument.allow_document_upload),
                  schemata='default',
        ),
    ]