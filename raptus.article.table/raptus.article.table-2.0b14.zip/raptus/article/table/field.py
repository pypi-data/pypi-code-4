from simplejson import dumps, loads
from zope.interface import implements
from AccessControl import ClassSecurityInfo

from Products.Archetypes.Field import LinesField
from Products.Archetypes.Registry import registerField

from raptus.article.table.utils import parseColumn
from raptus.article.table.widget import TableColumnsWidget
from raptus.article.table.interfaces import ITableColumnsField

class TableColumnsField(LinesField):
    _properties = LinesField._properties.copy()
    _properties.update({
        'type' : 'tablecolumns',
        'widget' : TableColumnsWidget,
        })

    implements(ITableColumnsField)

    security  = ClassSecurityInfo()

    security.declarePrivate('set')
    def set(self, instance, value, **kwargs):
        value = [dumps(column.copy()) for column in value if column['name'].strip() and not column.get('delete', 0)]
        LinesField.set(self, instance, value, **kwargs)

    security.declarePrivate('get')
    def get(self, instance, **kwargs):
        value = LinesField.get(self, instance, **kwargs) or ()
        columns = []
        for column in value:
            try:
                columns.append(loads(column))
            except: # BBB
                try:
                    columns.append(parseColumn(column))
                except:
                    pass
        return columns

registerField(TableColumnsField,
              title='TableColumnsField',
              description=('Used for storing table column definitions'))
