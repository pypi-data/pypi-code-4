from zope.interface import implements
from zope.component import adapts

from Products.Archetypes.interfaces import IObjectPostValidation

from raptus.article.table.interfaces import ITable
from raptus.article.core import RaptusArticleMessageFactory as _


class ValidateTableDefinitions(object):
    """ Validate the contenttype table. If no definition is selected and no columns are defined
        we receive a error. So this validator catch the problem.
    """
    
    implements(IObjectPostValidation)
    adapts(ITable)

    def __init__(self, context):
        self.context = context
        
    def __call__(self, request):
        
        definition = request.form.get('definition', None)
        columns = request.form.get('columns', [])
        
        if not definition and not columns:
            return dict(columns=_(u"Please select a table definition or type your own in this field."))
        
        # everything right :-)
        return None
