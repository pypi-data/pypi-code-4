# -*- coding: utf-8 -*- 
from __future__ import unicode_literals

from django.test import TestCase, RequestFactory
from django.utils import unittest

from rest_framework.compat import patterns, include, url

import nodetree
from nodetree.models import Node
from nodetree.viewsets import NodeViewSet
from nodetree.filters import microfilters

from .models import Town, Area, House

nodetree.autodiscover()
urlpatterns = patterns('',
    url(r'^nodetree/', include(nodetree.app.urls)),
)

factory = RequestFactory()
request = factory.get('/')


class TestNodeFilterSet(TestCase):

    urls = 'nodetree.tests.filters'

    def setUp(self):

        self.town = Town.objects.create(name='Zurich')
        self.town_node = Node.objects.create(node_type='town', content=self.town)

        self.area = Area.objects.create(name='Wiedikon')
        self.area_node = Node.objects.create(node_type='area', content=self.area, parent=self.town_node)

        self.area_2 = Area.objects.create(name='Seefeld')
        self.area_node_2 = Node.objects.create(node_type='area', content=self.area_2, parent=self.area_node)

        self.house = House.objects.create(name='Kalkbreitestrasse 98')
        self.house_node = Node.objects.create(node_type='house', content=self.house, parent=self.area_node_2)

    @unittest.skipUnless(microfilters, 'microfilters not installed')
    def test_node_type_filter(self):
        request = factory.get('/?node_type=town,area')
        view = NodeViewSet.as_view({'get': 'list'})
        response = view(request)

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
            },
            {
                'url': 'http://testserver/nodetree/node/3/',
                'parent': 'http://testserver/nodetree/node/2/',
                'content': {
                    'url': 'http://testserver/nodetree/area/2/',
                    'node': 'http://testserver/nodetree/node/3/',
                    'name': 'Seefeld'
                },
                'children': [
                    'http://testserver/nodetree/node/4/'
                ],
                'node_type': 'area',
                'level': 2
            }
        ]
        self.assertEqual(response.data, expected)

    @unittest.skipUnless(microfilters, 'microfilters not installed')
    def test_filter_custom_methods(self):
        request = factory.get('/?node_type=area')
        view = NodeViewSet.as_view({'get': 'ancestors'})
        response = view(request, pk=4)
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
                    'url': 'http://testserver/nodetree/area/2/',
                    'node': 'http://testserver/nodetree/node/3/',
                    'name': 'Seefeld'
                },
                'children': [
                    'http://testserver/nodetree/node/4/'
                ],
                'node_type': 'area',
                'level': 2
            }
        ]
        self.assertEqual(expected, response.data)


    @unittest.skipUnless(microfilters, 'microfilters not installed')
    def test_level_filter(self):
        request = factory.get('/?from_level=1&to_level=2')
        view = NodeViewSet.as_view({'get': 'list'})
        response = view(request, pk=4)
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
                    'url': 'http://testserver/nodetree/area/2/',
                    'node': 'http://testserver/nodetree/node/3/',
                    'name': 'Seefeld'
                },
                'children': [
                    'http://testserver/nodetree/node/4/'
                ],
                'node_type': 'area',
                'level': 2
            }
        ]
        self.assertEqual(expected, response.data)