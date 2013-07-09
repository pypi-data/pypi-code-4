# template's specific schema
from yams.buildobjs import RelationDefinition
from cubicweb.schema import RRQLExpression

class spent_for(RelationDefinition):
    subject = 'Expense'
    object = 'Workcase'
    cardinality = '?*'
    __permissions__ = {
        'read' : ('managers', 'users'),
        'add': ('managers', RRQLExpression('NOT (S in_state ST, ST name "accepted")')),
        'delete': ('managers', RRQLExpression('NOT (S in_state ST, ST name "accepted")')),
        }
