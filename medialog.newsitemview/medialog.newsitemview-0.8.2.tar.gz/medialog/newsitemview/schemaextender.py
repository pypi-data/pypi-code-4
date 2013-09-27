from zope.interface import implements
from zope.component import adapts
from zope.i18nmessageid import MessageFactory

from Products.Archetypes.public import StringField, BooleanField

from Products.ATContentTypes.interfaces.news import IATNewsItem
from Products.ATContentTypes.interface import IATFolder, IATTopic
from Products.Archetypes.atapi import SelectionWidget, BooleanWidget
from archetypes.schemaextender.interfaces import ISchemaExtender, IBrowserLayerAwareExtender 
from archetypes.schemaextender.field import ExtensionField
from medialog.newsitemview.interfaces import INewsitemObject, IFolderObject


_ = MessageFactory('medialog.newsitemview')


class _StringExtensionField (ExtensionField, StringField): 
    pass
        
class _BooleanExtensionField(ExtensionField, BooleanField):
	pass    

 
 

class ContentTypeExtender(object):
    """Adapter that adds custom data used for news item image size."""
    adapts(IATNewsItem)
    implements(ISchemaExtender, IBrowserLayerAwareExtender)
    layer = INewsitemObject
    _fields = [
        _StringExtensionField("newsitemsize",
            schemata = "settings",
            vocabulary_factory='medialog.newsitemview.ImageSizeVocabulary',
            default="preview",
            interfaces = (INewsitemObject,),
            widget = SelectionWidget(
                label = _(u"label_newsitemsize",
                    default=u"Size for news item image"),
                description = _(u"help_newsitemimage",
                    default=u"Choose Size"),
                ),
            ),
        ]

    def __init__(self, context):
    	self.context = context

    def getFields(self):
        return self._fields

class FolderTypeExtender(object):
    """Adapter that adds custom data used for image size."""
    adapts(IATFolder)
    implements(ISchemaExtender, IBrowserLayerAwareExtender)
    layer = IFolderObject
    _fields = [
        _StringExtensionField("folderimagesize",
            schemata = "settings",
            default="mini",
            vocabulary_factory='medialog.newsitemview.ImageSizeVocabulary',
            interfaces = (INewsitemObject,),
            widget = SelectionWidget(
                label = _(u"label_folderimagesize",
                    default=u"Size for image in summary view"),
                description = _(u"help_folderimagesize",
                    default=u"Choose Size"),
                ),
            ),
        _BooleanExtensionField("hide_images",
            schemata = "settings",
            interfaces = (INewsitemObject,),
            default = False,
            widget = BooleanWidget(
                label = _(u"label_hide_images",
                    default=u"Hide Images in the summary view"),
                description = _(u"help_hide_images",
                    default=u"Hide images from the folder view"),
                ),
            ),
        ]

        
    def __init__(self, context):
    	self.context = context

    def getFields(self):
        return self._fields


class TopicTypeExtender(object):
    """Adapter that adds custom data used for image size."""
    adapts(IATTopic)
    implements(ISchemaExtender, IBrowserLayerAwareExtender)
    layer = IFolderObject
    _fields = [
        _StringExtensionField("folderimagesize",
            schemata = "settings",
            vocabulary_factory='medialog.newsitemview.ImageSizeVocabulary',
            default="mini",
            interfaces = (INewsitemObject,),
            widget = SelectionWidget(
                label = _(u"label_folderimagesize",
                    default=u"Size for image in summary view"),
                description = _(u"help_folderimagesize",
                    default=u"Choose Size"),
                ),
            ),
        ]

        
    def __init__(self, context):
    	self.context = context

    def getFields(self):
        return self._fields

