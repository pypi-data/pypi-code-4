from zope.interface import implements

from archetypes.schemaextender.interfaces import ISchemaExtender
from archetypes.schemaextender.field import ExtensionField

from plone.indexer.interfaces import IIndexer

from Products.Archetypes import atapi

from raptus.article.media.interfaces import IVideo, IVideoEmbed
from raptus.article.core.componentselection import ComponentSelectionWidget
from raptus.article.core import RaptusArticleMessageFactory as _a


class LinesField(ExtensionField, atapi.LinesField):
    """ LinesField
    """


class VideoExtender(object):
    """ Adds the component selection field to the video content type
    """
    implements(ISchemaExtender)

    fields = [
        LinesField('components',
            enforceVocabulary = True,
            vocabulary_factory = 'componentselectionvocabulary',
            storage = atapi.AnnotationStorage(),
            schemata = 'settings',
            widget = ComponentSelectionWidget(
                description = _a(u'description_component_selection_article', default=u'Select the components in which this article should be displayed.'),
                label= _a(u'label_component_selection', default=u'Component selection'),
            )
        ),
    ]

    def __init__(self, context):
         self.context = context
         
    def getFields(self):
        return self.fields


class Index(object):
    implements(IIndexer)
    def __init__(self, obj, catalog):
        self.obj = obj
    def __call__(self):
        return self.obj.Schema()['components'].get(self.obj)
