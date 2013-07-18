# -*- coding: utf-8 -*-
"""
    odisea.CalipeNode
    ~~~~~~~~~~~~~~

    Este módulo contiene la clase CaliopeNode, que es el elemento atómico
    de la arquitectura de almancenamiento. Toda la información del sistema
    es contenida en elementos que heredan de  CaliopeNode.

    :author: Sebastián Ortiz <neoecos@gmail.com>
    :copyright: (c) 2013 por Fundación CorreLibre
    :license:  GNU AFFERO GENERAL PUBLIC LICENSE

Caliope Storage is the base of Caliope's Framework
Copyright (C) 2013  Fundación Correlibre

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU Affero General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Affero General Public License for more details.

    You should have received a copy of the GNU Affero General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""
from py2neo import neo4j
from neomodel.contrib import SemiStructuredNode
from neomodel.properties import (BooleanProperty,
                                 DateTimeProperty,
                                 FloatProperty,
                                 IntegerProperty,
                                 StringProperty)
from neomodel.relationship import RelationshipDefinition, RelationshipFrom
from StorageUtils import uuidGenerator, timeStampGenerator


class CaliopeNode(SemiStructuredNode):
    """
    This is the base class for all other items, contains basic properties and
    relations defined by the Caliope's Storage Model.
    This implements the basic operations defined in the model architecture.

    :class: CaliopeNode
    """

    uuid = StringProperty(default=uuidGenerator,
                             unique_index=True)

    #: All timestamps should be in UTC using pytz.utc
    timestamp = DateTimeProperty(default=timeStampGenerator)

    #:RelationshipTo previous node. Root nodes should use "ROOT"
    ancestor_node = RelationshipFrom('CaliopeNode', 'ANCESTOR_NODE')

    def __init__(self, *args, **kwargs):
        super(CaliopeNode, self).__init__(*args, **kwargs)
        self._set_node_attr(**kwargs)

    def _get_node_data(self):
        """
        This method read the metadata saved on a SemiStructuredNode and returns it.
        """
        rv = {}
        for attr in self.__node__.__metadata__['data']:
            rv[attr] = {'value': self.__node__.__metadata__['data'][attr]}
        return rv

    def _set_node_attr(self, **kwargs):
        """
        Method to update or add attributes to  the node.
        """
        for k in kwargs.keys():
            setattr(self, k, kwargs[k])

    def evolve(self, **kwargs):
        """
        Copy all predecessor node properties and update it with the new from the
        arguments, and set ancestor_node with the self uuid, and set the relationship
        with the ancestor.
        """
        cls = self.__class__
        new_node = cls(self._get_node_data())
        new_node._set_node_attr(**kwargs)
        new_node.save()
        new_node.ancestor_node.connect(self)
        return new_node

    @staticmethod
    def pull(id_node):
        return CaliopeNode.index.get(uuid=id_node)

    @classmethod
    def push(cls, **kwargs):
        """
        Creates a single node of one class and return it.
        """
        new_node = cls(**kwargs)
        new_node.save()
        return new_node


class CaliopeRelation(RelationshipDefinition):
    """
    This is the base class for relationships within CaliopeNodes, it may contain
    properties as in nodes.
    """
    OUTGOING = neo4j.Direction.OUTGOING
    INCOMING = neo4j.Direction.INCOMING
    EITHER = neo4j.Direction.EITHER


#Temporaly location

class CaliopeUser(CaliopeNode):

    username = StringProperty(index=True)
    domainname = StringProperty()
    password = StringProperty()




