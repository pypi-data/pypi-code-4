# -*- coding: utf-8 -*-
"""
    odisea.CaliopeNodeTest
    ~~~~~~~~~~~~~~

    Este módulo contiene funciones y clases que son utilizadas por
    el módelo de almacenamiento.

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
import unittest
import hashlib
from neomodel import DoesNotExist
from odisea.CaliopeStorage import CaliopeNode, CaliopeUser


class TestCaliopeNode(unittest.TestCase):

    def test_CaliopeNode_init_without_args(self):
        print "Test#1"
        print u"-" * 80
        node = CaliopeNode()
        node.save()
        print node.uuid, node.timestamp
        node2 = CaliopeNode.pull(node.uuid)
        assert node2.uuid == node.uuid
        print u"-" * 80

    def test_CaliopeNode_init_with_args(self):
        print "Test#2"
        print u"-" * 80
        props = {'foo': 'bar', 'other': 2}
        node = CaliopeNode(**props)
        node.save()
        print node.uuid, node.timestamp
        node.refresh()
        assert node.foo == 'bar' and node.other == 2
        print u"-" * 80

    def test_CaliopeNode_push(self):
        print "Test#3"
        print u"-" * 80
        props = {'foo': 'bar', 'other': 2}
        node = CaliopeNode.push(**props)
        print node.uuid, node.timestamp
        assert node.foo == 'bar' and node.other == 2
        print u"-" * 80

    def test_CaliopeNode_evolve(self):
        print "Test#4"
        print u"-" * 80
        props = {'foo': 'bar', 'other': 2}
        node = CaliopeNode.push(**props)
        print node.uuid, node.timestamp
        node = node.evolve(**{'foo': 'no_bar', 'other': 4})
        assert node.foo == 'no_bar' and node.other == 4
        print u"-" * 80

    def test_CaliopeNode_ancestor(self):
        print "Test#4"
        print u"-" * 80
        props = {'foo': 'bar', 'other': 2}
        node = CaliopeNode.push(**props)
        print node.uuid, node.timestamp
        node_next = node.evolve()
        node_prev = node_next.ancestor_node.single()
        assert node_prev == node


class TestCaliopeUser:
    """
    Test the CaliopeUser class
    """
    def test_CaliopeUser_creation(self):
        print "Test#5"
        print u"-" * 80
        u1 = CaliopeUser()
        u1.username = u'user'
        u1.password = hashlib.sha256(u'password').hexdigest()
        u1.domainname = u'correlibre.org'
        try:
            u2 = CaliopeUser.index.get(username=u'user')
            print u'username: ', u2.username, \
                  u'\npassword:', u2.password, \
                  u'\nuuid:', u2.uuid
            assert u1.password == u2.password
        except DoesNotExist:
            print u'User with username user will be created'
            assert u1.save() is not None
        print u"-" * 80

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()


