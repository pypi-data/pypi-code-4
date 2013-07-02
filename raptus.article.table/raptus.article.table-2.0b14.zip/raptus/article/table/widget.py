from AccessControl import ClassSecurityInfo

from Products.Archetypes.Registry import registerWidget
from Products.Archetypes.Widget import LinesWidget

class TableColumnsWidget(LinesWidget):
    _properties = LinesWidget._properties.copy()
    _properties.update({
        'macro' : "raptus_article_table_columns",
        'postback' : False,
        })

    security  = ClassSecurityInfo()

    security.declarePublic('columns')
    def columns(self, instance, field, request):
        if request.form.get(field.getName(), 0):
            columns = request.form.get(field.getName(), [])
        else:
            columns = instance.Schema()[field.getName()].get(instance)
        if not len(columns) or request.form.get('%s_add_column', 0):
            columns.append({})
        return columns

registerWidget(TableColumnsWidget,
               title='Table columns',
               description=('Renders a table to edit the columns of a table'),
               used_for=('raptus.article.table.field.TableColumnsField',)
               )
