from zope.component import adapts
from zope.interface import implements
from archetypes.schemaextender.interfaces import IBrowserLayerAwareExtender
from Products.Archetypes.atapi import StringField, SelectionWidget
from archetypes.schemaextender.field import ExtensionField
from wm.showhidecolumns.interfaces import IControlColumns, IShowHideColumnsLayer
from wm.showhidecolumns import ShowHideColumnsMessageFactory as _
from Products.Archetypes.utils import DisplayList

class ExtensionStringField(ExtensionField, StringField):
    """A string field"""    


COLUMN_VOCABULARY=DisplayList((
   ('0', _(u'vocab_show', default=u"Show column in any case")),
   ('1', _(u'vocab_hide', default=u"Hide column in any case")),
   ('default', _(u'vocab_default', default=u"Show column if not empty (default behaviour)")),
   ))
    
class ColumnsSchemaExtender(object):
    adapts(IControlColumns)
    implements(IBrowserLayerAwareExtender)

    def __init__(self, context):
        self.context = context

    
    layer = IShowHideColumnsLayer
         
    def getFields(self):
        
        fields = [
            ExtensionStringField('leftPortletslot',
                         required = False,
                         languageIndependent = True,
                         schemata = 'settings',
                         vocabulary=COLUMN_VOCABULARY,
                         enforce_vocabulary=True,
                         widget = SelectionWidget(
                                  description=_(u'help_column', default=u"allows to show or hide the portlet column"),
                                  label = _(u"label_column_left", default=u"Left portlet slot visibility"),
                                  visible={'view' : 'hidden',
                                           'edit' : 'visible'},
                                  ),
            ),
            
            ExtensionStringField('rightPortletslot',
                         required = False,
                         languageIndependent = True,
                         schemata = 'settings',
                         vocabulary=COLUMN_VOCABULARY,
                         enforce_vocabulary=True,
                         widget = SelectionWidget(
                                  description=_(u'help_column', default=u"allows to show or hide the portlet column"),
                                  label = _(u"label_column_right", default=u"Right portlet slot visibility"),
                                  visible={'view' : 'hidden',
                                           'edit' : 'visible'},
                                  ),
            ),
            
        ]
        
        return fields