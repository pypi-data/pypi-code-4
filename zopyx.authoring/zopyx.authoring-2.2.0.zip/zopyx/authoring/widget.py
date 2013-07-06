
from AccessControl import ClassSecurityInfo
from Products.Archetypes import atapi
from Products.Archetypes.Registry import registerWidget

class SortableInAndOutWidget(atapi.InAndOutWidget):
    _properties = atapi.InAndOutWidget._properties.copy()
    _properties.update({
        'macro' : "sortable_inandout",
        'size' : '6',
        'helper_js': ('widgets/js/inandout.js','select_lists.js'),
        })

    security = ClassSecurityInfo()


registerWidget(SortableInAndOutWidget,
               title='String',
               description=('Sortable InAndOutWidget'),
               used_for=('Products.Archetypes.Field.LinesField',)
               )
