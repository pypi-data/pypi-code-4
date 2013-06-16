# -*- coding: utf-8 -*- 
from __future__ import unicode_literals
import nodetree
from .models import Town, Area, House, Person

class TownNodeType(nodetree.NodeType):

    name = 'town'
    model_class = Town

    is_root = True
    allowed_children = ['area', 'house', 'person']


class AreaNodeType(nodetree.NodeType):

    name = 'area'
    model_class = Area

    allowed_children = ['house', 'person', 'area']


class HouseNodeType(nodetree.NodeType):

    name = 'house'
    model_class = House
    allowed_children = ['person']


class PersonNodeType(nodetree.NodeType):

    name = 'person'
    model_class = Person
    is_root = True
    is_leaf = True

nodetree.app.register(TownNodeType)
nodetree.app.register(AreaNodeType)
nodetree.app.register(HouseNodeType)
nodetree.app.register(PersonNodeType)