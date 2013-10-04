
from App.class_init import InitializeClass
from Products.Archetypes.public import TextAreaWidget
from Products.Archetypes.Registry import registerWidget

class PreTextAreaWidget(TextAreaWidget):
    """ A TextAreaWidget for preformatted text """

    _properties = TextAreaWidget._properties.copy()
    _properties.update({
        'macro' : "pretextareawidget",
        })


InitializeClass(PreTextAreaWidget)

registerWidget(PreTextAreaWidget,
               title='PreTextAreaWidget',
               description='PreTextAreaPreWidget',
               used_for=('Products.Archetypes.Field.StringField',)
               )


