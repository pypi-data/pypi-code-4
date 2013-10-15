from yams.buildobjs import (EntityType, RelationDefinition,
                            SubjectRelation, String, Float, Date)

from cubicweb.schema import WorkflowableEntityType, ERQLExpression, RRQLExpression
from cubes.workorder.schema import WorkOrder

_ = unicode


class Activity(WorkflowableEntityType):
    """time someone spent working on something
    """
    __permissions__ = {'read' : ('managers', 'users'),
                       'update' : ('managers', ERQLExpression('X in_state ST, ST name "pending", X owned_by U')),
                       'delete' : ('managers', ERQLExpression('X in_state ST, ST name "pending", X owned_by U')),
                       'add' : ('managers', 'users'),
                       }
    duration = Float(required=True, default=1.0)
    diem = Date(default='TODAY', required=True)
    description = String(fulltextindexed=True, maxsize=256)


class Resourcetype(EntityType):
    """see projman"""
    title = String(required=True, maxsize=64)


class Resource(EntityType):
    """see projman"""
    title = String(required=True, unique=True, maxsize=64)
    rate = Float()
    rtype = SubjectRelation('Resourcetype', cardinality='1*')
    use_calendar = SubjectRelation('Calendaruse', cardinality='+?', composite='subject')
    euser = SubjectRelation('CWUser', cardinality='??')


class done_by(RelationDefinition):
    """activity performed by a Resource"""
    __permissions__ = {'read' : ('managers', 'users'),
                       'delete' : ('managers', RRQLExpression('S in_state ST, ST name "pending", O euser U')),
                       'add' : ('managers', RRQLExpression('O euser U'),),
                       }
    subject = 'Activity'
    object = 'Resource'
    cardinality = '1*'
    constraints = [RQLVocabularyConstraint('O euser U?, U in_state S, NOT S name "deactivated"')]

class done_for(RelationDefinition):
    subject = 'Activity'
    object = 'WorkOrder'
    cardinality = '1*'


class todo_by(RelationDefinition):
    subject = 'WorkOrder'
    object = 'Resource'
    cardinality = '+*'
    constraints = [RQLVocabularyConstraint('O euser U?, U in_state S, NOT S name "deactivated"')]

