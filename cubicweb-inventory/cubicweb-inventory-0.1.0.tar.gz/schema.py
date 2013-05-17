"""inventory application'schema

:organization: Logilab
:copyright: 2003-2011 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
"""
__docformat__ = "restructuredtext en"

from yams.buildobjs import (EntityType, RelationDefinition, SubjectRelation,
                            String, Date, Int, Float)
from cubicweb.schema import WorkflowableEntityType

from cubes.link.schema import Link

_ = unicode

PERMISSIONS = {'read':   ('managers', 'users', 'guests',),
               'add':    ('managers', ),
               'update': ('managers', 'owners',),
               'delete': ('managers', 'owners'),
               }

Link.__permissions__ = PERMISSIONS


class DeviceModel(WorkflowableEntityType):
    name = String(required=True, fulltextindexed=True, unique=False,
                  maxsize=64, description=_('Commercial name, short description of the device model')
                  )

    made_by = SubjectRelation('Company', cardinality='?*', description=_('Manufacturer'))

    model_ref = String(required=False, fulltextindexed=True, unique=False,
                       maxsize=64, description=_('Model (reference)')
                       )

    klass = String(vocabulary=('server',
                               'desktop',
                               'thinclient',
                               'laptop',
                               'display',
                               'printer',
                               'switch',
                               'net appliance',
                               'storage',
                               'power supply',
                               'consumable',
                               'other',
                               ),
                   description=_('Indicates the general class of this device'))

    description = String(fulltextindexed=True,
                         description=_('Detailed description of the device model'))

    deprecation_duration = Int(default=5, description=_('Deprectation duration (in years)'))


class Device(WorkflowableEntityType):
    name = String(required=True, fulltextindexed=True, unique=False,
                  maxsize=64, description=_('Internal name or short description of the device')
                  )

    model = SubjectRelation('DeviceModel', cardinality='?*', description=_('Model'))

    supplier = SubjectRelation('Company', cardinality='?*', description=_('Manufacturer'))

    serial  = String(required=True, fulltextindexed=True, unique=True,
                     maxsize=128, description=_('Device serial number')
                     )

    purchased_on = Date(description=_('Purchase date'), required=False)

    purchase_price = Float(description=_('Purchase price (ex. VAT)'))

    description = String(fulltextindexed=True,
                         description=_('Detailed description of the device'))

    installed_in = SubjectRelation('Device', cardinality='*?',
                                   description=_('Device (eg. a server) in which this device has been installed'))

    situated_in = SubjectRelation('Zone', cardinality='?*')

    warranty_expires_on = Date(description=_('End of waranty'))


class comments(RelationDefinition):
    subject = 'Comment'
    object = ('Device', 'DeviceModel')


class tags(RelationDefinition):
    subject = 'Tag'
    object = ('Device', 'DeviceModel')
