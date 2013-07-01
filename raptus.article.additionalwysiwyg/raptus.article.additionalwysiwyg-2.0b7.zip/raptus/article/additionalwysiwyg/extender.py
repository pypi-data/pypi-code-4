from zope.interface import implements
from zope.component import adapts

from archetypes.schemaextender.interfaces import ISchemaExtender
from archetypes.schemaextender.field import ExtensionField

from Products.Archetypes import atapi
from Products.ATContentTypes.configuration import zconf
from Products.ATContentTypes import ATCTMessageFactory as _at

from raptus.article.core import RaptusArticleMessageFactory as _
from raptus.article.core.interfaces import IArticle

class TextField(ExtensionField, atapi.TextField):
    """ TextField
    """
    
class ArticleExtender(object):
    """ Adds the additional WYSIWYG text field to the article schema
    """
    implements(ISchemaExtender)
    adapts(IArticle)

    fields = [
        TextField('additional-text',
            required=False,
            searchable=True,
            storage = atapi.AnnotationStorage(),
            validators = ('isTidyHtmlWithCleanup',),
            default_output_type = 'text/x-html-safe',
            widget = atapi.RichWidget(
                description = '',
                label = _(u'label_additional_text', default=u'Additional Text'),
                rows = 15,
                allow_file_upload = zconf.ATDocument.allow_document_upload),
        ),
    ]

    def __init__(self, context):
         self.context = context
         
    def getFields(self):
        return self.fields
