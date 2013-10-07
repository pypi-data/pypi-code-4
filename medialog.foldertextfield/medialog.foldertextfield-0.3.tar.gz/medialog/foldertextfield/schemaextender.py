from zope.interface import implements
from zope.component import adapts
from zope.i18nmessageid import MessageFactory

from Products.Archetypes.public import TextField
from Products.ATContentTypes.interface import IATFolder
from Products.Archetypes.atapi import RichWidget

from archetypes.schemaextender.interfaces import ISchemaExtender, IBrowserLayerAwareExtender 
from archetypes.schemaextender.field import ExtensionField

from medialog.foldertextfield.interfaces import IFolderTextObject
#, IFolderTextEnabled



_ = MessageFactory('medialog.foldertextfield')


class _TextExtensionField(ExtensionField, TextField):
	pass    



class FolderTextExtender(object):
    """Adapter that adds a body text field."""
    adapts(IFolderTextObject)
    implements(ISchemaExtender, IBrowserLayerAwareExtender)
    layer = IFolderTextObject
    _fields = [
        _TextExtensionField("text",
            schemata = "default",
            required=False,
            searchable=True,
            primary=True,
            validators=('isTidyHtmlWithCleanup',),
            default_output_type='text/x-html-safe',
            widget=RichWidget(
                        description='',
                        label=_(u'label_body_text', default=u'Body Text'),
                        rows=25,
            ),
        ),
    ]

        
    def __init__(self, context):
    	self.context = context

    def getFields(self):
        return self._fields
 