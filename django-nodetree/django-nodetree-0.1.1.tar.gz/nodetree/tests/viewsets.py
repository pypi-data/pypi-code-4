# -*- coding: utf-8 -*- 
from __future__ import unicode_literals
import json

from django.test import TestCase, RequestFactory

from rest_framework.compat import patterns, include, url

import nodetree
from nodetree.models import Node

from .models import Town, Area, House
from nodetree.viewsets import NodeViewSet

nodetree.autodiscover()
urlpatterns = patterns('',
    url(r'^nodetree/', include(nodetree.app.urls)),
)

factory = RequestFactory()
request = factory.get('/')

class TestNodeListView(TestCase):

    urls = 'nodetree.tests.viewsets'

    def setUp(self):
        self.town_1 = Town.objects.create(name='Zurich')
        self.town_node_1 = Node.objects.create(node_type='town', content=self.town_1)

        self.town_2 = Town.objects.create(name='Bern')
        self.town_node_2 = Node.objects.create(node_type='town', content=self.town_2)

        self.town_3 = Town.objects.create(name='Lucerne')
        self.town_node_3 = Node.objects.create(node_type='town', content=self.town_3)
        self.view = NodeViewSet.as_view({'get': 'list', 'post': 'create'})

    def test_get_list(self):
        request = factory.get('/')
        response = self.view(request)
        expected = [
            {
                'url': 'http://testserver/nodetree/node/1/',
                'parent': None,
                'children': [],
                'content': {
                    'url': 'http://testserver/nodetree/town/1/',
                    'node': 'http://testserver/nodetree/node/1/',
                    'name': 'Zurich'
                },
                'node_type': 'town',
                'level': 0
            },
            {
                'url': 'http://testserver/nodetree/node/2/',
                'parent': None,
                'children': [],
                'content': {
                    'url': 'http://testserver/nodetree/town/2/',
                    'node': 'http://testserver/nodetree/node/2/',
                    'name': 'Bern'
                },
                'node_type': 'town',
                'level': 0

            },
            {
                'url': 'http://testserver/nodetree/node/3/',
                'parent': None,
                'children': [],
                'content': {
                    'url': 'http://testserver/nodetree/town/3/',
                    'node': 'http://testserver/nodetree/node/3/',
                    'name': 'Lucerne'
                },
                'node_type': 'town',
                'level': 0
            }
        ]
        self.assertEqual(expected, response.data)

    def test_invalid_post_list(self):
        request = factory.post('/', data={'node_type': 'foo'})
        response = self.view(request)
        expected = {
            'content': ['This field is required.'],
            'node_type': ["Node type 'foo' does not exist."]
        }
        self.assertEqual(expected, response.data)

    def test_post_list(self):
        request = factory.post('/', json.dumps({
                'node_type': 'area',
                'target': 'http://testserver/nodetree/node/1/',
                'position': 'first-child',
                'content': {
                    'name': 'Wiedikon',
                }
            }), content_type='application/json')
        response = self.view(request)

        expected = {
            'url': 'http://testserver/nodetree/node/4/',
            'parent': 'http://testserver/nodetree/node/1/',
            'children': [],
            'content': {
                'url': 'http://testserver/nodetree/area/1/',
                'node': 'http://testserver/nodetree/node/4/',
                'name': 'Wiedikon'
            },
            'node_type': 'area',
            'level': 1
        }
        self.assertEqual(expected, response.data)
        self.assertEqual(Area.objects.get(pk=1).name, 'Wiedikon')



class TestNodeDetailView(TestCase):

    urls = 'nodetree.tests.viewsets'

    def setUp(self):
        self.town_1 = Town.objects.create(name='Zurich')
        self.town_node_1 = Node.objects.create(node_type='town', content=self.town_1)

        self.town_2 = Town.objects.create(name='Bern')
        self.town_node_2 = Node.objects.create(node_type='town', content=self.town_2)

        self.town_3 = Town.objects.create(name='Lucerne')
        self.town_node_3 = Node.objects.create(node_type='town', content=self.town_3)

        self.area = Area.objects.create(name='Elfenau')
        self.area_node = Node.objects.create(node_type='area', content=self.area)
        self.view = NodeViewSet.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'})

    def test_get_detail(self):
        request = factory.get('/')
        response = self.view(request, pk=1)
        expected = {
            'url': 'http://testserver/nodetree/node/1/',
            'parent': None,
            'children': [],
            'content': {
                'url': 'http://testserver/nodetree/town/1/',
                'node': 'http://testserver/nodetree/node/1/',
                'name': 'Zurich'
            },
            'node_type': 'town',
            'level': 0
        }
        self.assertEqual(expected, response.data)

    def test_invalid_put_detail(self):
        request = factory.put('/', json.dumps({
           'node_type': 'area',
           'target': 'http://testserver/nodetree/node/2/',
           'position': 'first-child',
        }), content_type='application/json')

        response = self.view(request, pk=1)
        expected = {
            'non_field_errors': [
                "You can't add node type 'town' as child of 'town'."
            ]
        }
        self.assertEqual(expected, response.data)

    def test_put_detail(self):
        request = factory.put('/', json.dumps({
           'target': 'http://testserver/nodetree/node/1/',
           'position': 'first-child',
        }), content_type='application/json')

        response = self.view(request, pk=4)
        expected = {
            'url': 'http://testserver/nodetree/node/4/',
            'parent': 'http://testserver/nodetree/node/1/',
            'children': [],
            'content': {
                'url': 'http://testserver/nodetree/area/1/',
                'node': 'http://testserver/nodetree/node/4/',
                'name': 'Elfenau'
            },
            'node_type': 'area',
            'level': 1
        }
        self.assertEqual(expected, response.data)

    def test_delete_detail(self):
        request = factory.delete('/')
        response = self.view(request, pk=3)

        self.assertEqual(204, response.status_code)
        self.assertEqual(Node.objects.count(), 3)


class TestCustomNodeDetailMethods(TestCase):

    urls = 'nodetree.tests.viewsets'

    def setUp(self):
        self.town = Town.objects.create(name='Zurich')
        self.town_node = Node.objects.create(node_type='town', content=self.town)

        self.area = Area.objects.create(name='Wiedikon')
        self.area_node = Node.objects.create(node_type='area', content=self.area, parent=self.town_node)

        self.house = House.objects.create(name='Kalkbreitestrasse 98')
        self.house_node = Node.objects.create(node_type='house', content=self.house, parent=self.area_node)

    def test_invalid_ancestors(self):
        request = factory.get('/')
        view = NodeViewSet.as_view({'get': 'ancestors'})
        response = view(request, pk=16)
        self.assertEqual(response.status_code, 404)

    def test_invalid_descendants(self):
        request = factory.get('/')
        view = NodeViewSet.as_view({'get': 'descendants'})
        response = view(request)
        self.assertEqual(response.status_code, 404)

    def test_invalid_children(self):
        request = factory.get('/')
        view = NodeViewSet.as_view({'get': 'children'})
        response = view(request)
        self.assertEqual(response.status_code, 404)

    def test_invalid_siblings(self):
        request = factory.get('/')
        view = NodeViewSet.as_view({'get': 'siblings'})
        response = view(request)
        self.assertEqual(response.status_code, 404)

    def test_valid_ancestors(self):
        request = factory.get('/')
        view = NodeViewSet.as_view({'get': 'ancestors'})
        response = view(request, pk=3)
        expected = [
            {
                'url': 'http://testserver/nodetree/node/1/',
                'parent': None,
                'content': {
                    'url': 'http://testserver/nodetree/town/1/',
                    'node': 'http://testserver/nodetree/node/1/',
                    'name': 'Zurich'
                },
                'children': [
                    'http://testserver/nodetree/node/2/'
                ],
                'node_type': 'town',
                'level': 0
            },
            {
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
            }
        ]
        self.assertEqual(expected, response.data)

    def test_valid_descendants(self):
        request = factory.get('/')
        view = NodeViewSet.as_view({'get': 'descendants'})
        response = view(request, pk=1)
        expected = [
            {
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
            },
            {
                'url': 'http://testserver/nodetree/node/3/',
                'parent': 'http://testserver/nodetree/node/2/',
                'content': {
                    'url': 'http://testserver/nodetree/house/1/',
                    'node': 'http://testserver/nodetree/node/3/',
                    'name': 'Kalkbreitestrasse 98'
                },
                'children': [],
                'node_type': 'house',
                'level': 2
            },
        ]
        self.assertEqual(expected, response.data)

    def test_valid_children(self):
        request = factory.get('/')
        view = NodeViewSet.as_view({'get': 'children'})
        response = view(request, pk=1)
        expected = [
            {
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
            },
        ]
        self.assertEqual(expected, response.data)


    def test_valid_siblings(self):

        area = Area.objects.create(name='Seefeld')
        area_node = Node(node_type='area', content=area)
        area_node.insert_at(self.area_node, 'left', save=True)

        area_2 = Area.objects.create(name='Wollishofen')
        area_node_2 = Node(node_type='area', content=area_2)
        area_node_2.insert_at(self.area_node, 'right', save=True)

        request = factory.get('/')
        view = NodeViewSet.as_view({'get': 'siblings'})
        response = view(request, pk=self.area_node.pk)
        expected = [
            {
                'url': 'http://testserver/nodetree/node/4/',
                'parent': 'http://testserver/nodetree/node/1/',
                'content': {
                    'url': 'http://testserver/nodetree/area/2/',
                    'node': 'http://testserver/nodetree/node/4/',
                    'name': 'Seefeld'
                },
                'children': [],
                'node_type': 'area',
                'level': 1
            },
            {
                'url': 'http://testserver/nodetree/node/5/',
                'parent': 'http://testserver/nodetree/node/1/',
                'content': {
                    'url': 'http://testserver/nodetree/area/3/',
                    'node': 'http://testserver/nodetree/node/5/',
                    'name': 'Wollishofen'
                },
                'children': [],
                'node_type': 'area',
                'level': 1
            },
        ]
        self.assertEqual(expected, response.data)

    def test_valid_root(self):
        request = factory.get('/')
        view = NodeViewSet.as_view({'get': 'root'})
        response = view(request, pk=3)
        expected = {
            'url': 'http://testserver/nodetree/node/1/',
            'parent': None,
            'content': {
                'url': 'http://testserver/nodetree/town/1/',
                'node': 'http://testserver/nodetree/node/1/',
                'name': 'Zurich'
            },
            'children': [
                'http://testserver/nodetree/node/2/'
            ],
            'node_type': 'town',
            'level': 0
        }
        self.assertEqual(expected, response.data)


class TestDepthQueryParameter(TestCase):

    urls = 'nodetree.tests.viewsets'

    def setUp(self):
        self.town = Town.objects.create(name='Zurich')
        self.town_node = Node.objects.create(node_type='town', content=self.town)

        self.area = Area.objects.create(name='Wiedikon')
        self.area_node = Node.objects.create(node_type='area', content=self.area, parent=self.town_node)

        self.house = House.objects.create(name='Kalkbreitestrasse 98')
        self.house_node = Node.objects.create(node_type='house', content=self.house, parent=self.area_node)

    def test_invalid_depth_param(self):
        request = factory.get('/?depth=foobar')
        view = NodeViewSet.as_view({'get': 'retrieve'})
        response = view(request, pk=1)
        self.assertEqual(response.status_code, 400)

    def test_get_detail(self):
        request = factory.get('/?depth=1')
        view = NodeViewSet.as_view({'get': 'retrieve'})
        response = view(request, pk=1)
        expected = {
            'url': 'http://testserver/nodetree/node/1/',
            'parent': None,
            'children': [{
                 'url': 'http://testserver/nodetree/node/2/',
                 'parent': 'http://testserver/nodetree/node/1/',
                 'children': [
                     'http://testserver/nodetree/node/3/',
                 ],
                 'content': {
                     'url': 'http://testserver/nodetree/area/1/',
                     'node': 'http://testserver/nodetree/node/2/',
                     'name': 'Wiedikon'
                 },
                 'node_type': 'area',
                 'level': 1
            }],
            'content': {
                'url': 'http://testserver/nodetree/town/1/',
                'node': 'http://testserver/nodetree/node/1/',
                'name': 'Zurich'
            },
            'node_type': 'town',
            'level': 0
        }
        self.assertEqual(expected, response.data)