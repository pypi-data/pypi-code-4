from __future__ import unicode_literals

from django.test import TestCase, RequestFactory

from rest_framework.compat import patterns, url, include

import nodetree
from nodetree.models import Node

from .models import Town, Person, House, Area

nodetree.autodiscover()
urlpatterns = patterns('',
    url(r'^nodetree/', include(nodetree.app.urls)),
)

factory = RequestFactory()
request = factory.get('/')  # Just to ensure we have a request in the serializer context

class TestContentSerializer(TestCase):

    urls = 'nodetree.tests.serializers'

    def setUp(self):
        self.content_obj = Town.objects.create(name='Zurich')
        self.node_obj = Node.objects.create(node_type='town', content=self.content_obj)

    def test_serialization(self):
        serializer = nodetree.app.get_node_type('town').serializer_class(self.content_obj, context={'request': request})
        expected = {
            'url': 'http://testserver/nodetree/town/1/',
            'node': 'http://testserver/nodetree/node/1/',
            'name': 'Zurich'
        }
        self.assertEqual(expected, serializer.data)


class TestBaseNodeSerializer(TestCase):

    urls = 'nodetree.tests.serializers'

    def setUp(self):
        self.content_obj = Town.objects.create(name='Zurich')
        self.node_obj = Node.objects.create(node_type='town', content=self.content_obj)

        self.node_serializer_class = nodetree.app.get_node_serializer_class(depth=-1)

    def test_serialization(self):
        serializer = self.node_serializer_class(self.node_obj, context={'request': request})
        expected = {
            'url': 'http://testserver/nodetree/node/1/',
            'content': {
                'url': 'http://testserver/nodetree/town/1/',
                'node': 'http://testserver/nodetree/node/1/',
                'name': 'Zurich',
            },
            'parent': None,
            'children': [],
            'node_type': 'town',
        }
        self.assertEqual(expected, serializer.data)


class TestBaseNodeSerializer(TestCase):

    urls = 'nodetree.tests.serializers'

    def setUp(self):
        self.content_obj = Town.objects.create(name='Zurich')
        self.node_obj = Node.objects.create(node_type='town', content=self.content_obj)
        self.node_serializer_class = nodetree.app.get_node_serializer_class(depth=-1)

    def test_serialization(self):
        serializer = self.node_serializer_class(self.node_obj, context={'request': request})
        expected = {
            'url': 'http://testserver/nodetree/node/1/',
            'content': {
                'url': 'http://testserver/nodetree/town/1/',
                'node': 'http://testserver/nodetree/node/1/',
                'name': 'Zurich',
            },
            'parent': None,
            'children': [],
            'node_type': 'town',
            'level': 0
        }
        self.assertEqual(expected, serializer.data)


class TestUpdateNodeSerializer(TestCase):

    urls = 'nodetree.tests.serializers'

    def setUp(self):
        self.town = Town.objects.create(name='Zurich')
        self.town_node = Node.objects.create(node_type='town', content=self.town)

        self.area = Town.objects.create(name='Wiedikon')
        self.area_node = Node(node_type='area', content=self.area)
        self.area_node.insert_at(self.town_node, 'first-child', True)

        self.house = House.objects.create(name='Kalkbreitestrasse 98')
        self.house_node = Node(node_type='house', content=self.house)
        self.house_node.insert_at(self.area_node, 'first-child', True)

        self.person = Person.objects.create(first_name='Lukas', last_name='Buenger')
        self.person_node = Node(node_type='person', content=self.person)
        self.person_node.insert_at(self.house_node, 'first-child', True)

        self.node_serializer_class = nodetree.app.get_node_serializer_class(depth=-1)
        self.update_node_serializer_class = nodetree.app.get_update_node_serializer_class(depth=-1)

    def test_non_existing_target(self):
        serializer = self.update_node_serializer_class(self.house_node, data={}, context={'request': request})
        serializer.is_valid()
        expected = {
            'non_field_errors': ["Node type 'house' can't be used as root."]
        }
        self.assertEqual(serializer.errors, expected)

    def test_non_existing_position(self):
        serializer = self.update_node_serializer_class(self.house_node, data={
            'target': 'http://testserver/nodetree/node/1/'
        }, context={'request': request})
        serializer.is_valid()
        expected = {
            'non_field_errors': ["You have to provide a 'position' in combination with a 'target'."]
        }
        self.assertEqual(serializer.errors, expected)

    def test_invalid_target(self):
        serializer = self.update_node_serializer_class(self.house_node, data={
            'target': 'http://testserver/nodetree/node/3/',
            'position': 'first-child',
        }, context={'request': request})
        serializer.is_valid()
        expected = {
            'non_field_errors': ["You can't use the object you want to move as target."]
        }
        self.assertEqual(serializer.errors, expected)

    def test_invalid_parent_due_to_position_interpretation(self):
        serializer = self.update_node_serializer_class(self.house_node, data={
            'target': 'http://testserver/nodetree/node/1/',
            'position': 'left',
        }, context={'request': request})
        serializer.is_valid()
        expected = {
            'non_field_errors': ["Node type 'house' can't be used as root."]
        }
        self.assertEqual(serializer.errors, expected)

    def test_invalid_parent(self):
        serializer = self.update_node_serializer_class(self.area_node, data={
            'target': 'http://testserver/nodetree/node/2/',
            'position': 'first-child',
        }, context={'request': request})
        serializer.is_valid()
        expected = {
            'non_field_errors': ["You can't use the object you want to move as target."]
        }
        self.assertEqual(serializer.errors, expected)

    def test_valid_parent(self):
        serializer = self.update_node_serializer_class(self.house_node, data={
            'target': 'http://testserver/nodetree/node/2/',
            'position': 'left',
        }, context={'request': request})
        serializer.is_valid()
        serializer.save()
        expected = {
            'url': 'http://testserver/nodetree/node/3/',
            'parent': 'http://testserver/nodetree/node/1/',
            'children': [
                {
                    'url': 'http://testserver/nodetree/node/4/',
                    'parent': 'http://testserver/nodetree/node/3/',
                    'children': [],
                    'content': {
                        'url': 'http://testserver/nodetree/person/1/',
                        'node': 'http://testserver/nodetree/node/4/',
                        'first_name': 'Lukas',
                        'last_name': 'Buenger'
                    },
                    'node_type': 'person',
                    'level': 2
                }
            ],
            'content':
                {
                    'url': 'http://testserver/nodetree/house/1/',
                    'node': 'http://testserver/nodetree/node/3/',
                    'name': 'Kalkbreitestrasse 98'
                },
            'node_type': 'house',
            'level': 1
        }
        self.assertEqual(expected, serializer.data)


class TestCreateNodeSerializer(TestCase):

    urls = 'nodetree.tests.serializers'

    def setUp(self):
        self.town = Town.objects.create(name='Zurich')
        self.town_node = Node.objects.create(node_type='town', content=self.town)

        self.area = Area.objects.create(name='Wiedikon')
        self.area_node = Node(node_type='area', content=self.area)
        self.area_node.insert_at(self.town_node, 'first-child', True)

        self.house = House.objects.create(name='Kalkbreitestrasse 98')
        self.house_node = Node(node_type='house', content=self.house)
        self.house_node.insert_at(self.area_node, 'first-child', True)

        self.person = Person.objects.create(first_name='Lukas', last_name='Buenger')
        self.person_node = Node(node_type='person', content=self.person)
        self.person_node.insert_at(self.house_node, 'first-child', True)
        self.node_serializer_class = nodetree.app.get_node_serializer_class(depth=-1)

        self.create_node_serializer_class = nodetree.app.get_create_node_serializer_class(depth=-1)

    def test_non_existing_node_type(self):
        serializer = self.create_node_serializer_class(data={}, context={'request': request})
        serializer.is_valid()

        expected = {'node_type': ['This field is required.'], 'content': ['This field is required.']}
        self.assertEqual(expected, serializer.errors)

    def test_invalid_node_type(self):
        serializer = self.create_node_serializer_class(data={'node_type': 'foo'}, context={'request': request})
        serializer.is_valid()

        expected = {'node_type': ["Node type 'foo' does not exist."], 'content': ['This field is required.']}
        self.assertEqual(expected, serializer.errors)

    def test_non_existing_content(self):
        serializer = self.create_node_serializer_class(data={'node_type': 'person'}, context={'request': request})
        serializer.is_valid()

        expected = {'content': ['This field is required.']}
        self.assertEqual(expected, serializer.errors)

    def test_invalid_content(self):
        serializer = self.create_node_serializer_class (data={
            'node_type': 'person',
            'content': {
                'first_name': 'Lukas',
                'last_name': '',
            }
        }, context={'request': request})
        serializer.is_valid()
        expected = {'content': [
                {'last_name': ['This field is required.']}
            ]
        }
        self.assertEqual(expected, serializer.errors)

    def test_valid_content(self):
        serializer = self.create_node_serializer_class (data={
            'node_type': 'person',
            'content': {
                'first_name': 'Lukas',
                'last_name': 'Buenger',
            }
        }, context={'request': request})
        serializer.is_valid()
        serializer.save()
        expected = {
            'url': 'http://testserver/nodetree/node/5/',
            'parent': None,
            'children': [],
            'node_type': 'person',
            'content': {
                'url': 'http://testserver/nodetree/person/2/',
                'node': 'http://testserver/nodetree/node/5/',
                'first_name': 'Lukas',
                'last_name': 'Buenger',
            },
            'level': 0
        }
        self.assertEqual(expected, serializer.data)


class TestDepthParameter(TestCase):

    urls = 'nodetree.tests.serializers'

    def setUp(self):
        self.town = Town.objects.create(name='Zurich')
        self.town_node = Node.objects.create(node_type='town', content=self.town)

        self.area = Area.objects.create(name='Wiedikon')
        self.area_node = Node(node_type='area', content=self.area)
        self.area_node.insert_at(self.town_node, 'first-child', True)

        self.house = House.objects.create(name='Kalkbreitestrasse 98')
        self.house_node = Node(node_type='house', content=self.house)
        self.house_node.insert_at(self.area_node, 'first-child', True)

        self.person = Person.objects.create(first_name='Lukas', last_name='Buenger')
        self.person_node = Node(node_type='person', content=self.person)
        self.person_node.insert_at(self.house_node, 'first-child', True)
        self.node_serializer_class = nodetree.app.get_node_serializer_class(depth=1)

    def test_max_depth(self):
        serializer = self.node_serializer_class(self.town_node, context={'request': request})
        expected = {
            'url': 'http://testserver/nodetree/node/1/',
            'parent': None, 
            'content': {
                'url': 'http://testserver/nodetree/town/1/',
                'node': 'http://testserver/nodetree/node/1/',
                'name': 'Zurich'
            }, 
            'children': [{
                    'url': 'http://testserver/nodetree/node/2/',
                    'parent': 'http://testserver/nodetree/node/1/',
                    'content': {
                        'url': 'http://testserver/nodetree/area/1/',
                        'node': 'http://testserver/nodetree/node/2/',
                        'name': 'Wiedikon'
                    }, 
                    'children': [
                        'http://testserver/nodetree/node/3/'
                    ], 
                    'node_type': 'area',
                    'level': 1
            }], 
            'node_type': 'town',
            'level': 0
        }
        self.assertEqual(serializer.data, expected)