# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import json

from django.contrib.auth.models import Permission, User
from django.test import TestCase, Client

from rest_framework.compat import patterns, include, url

import nodetree
from nodetree.models import Node
from nodetree.permissions import NodeTreeModelPermissions
from nodetree.viewsets import NodeViewSet

from .models import Town, Area, House

nodetree.autodiscover()
urlpatterns = patterns('',
    url(r'^nodetree/node/$', NodeViewSet.as_view(
            {'get': 'list', 'post': 'create'},
            permission_classes = (NodeTreeModelPermissions, )
        ), name='node-list'),
    url(r'^nodetree/node/(?P<pk>[0-9]+)/$', NodeViewSet.as_view(
            actions={'get': 'retrieve', 'put': 'update', 'delete': 'destroy'},
            permission_classes = (NodeTreeModelPermissions, )
        ), name='node-detail'),
    url(r'^nodetree/', include(nodetree.app.urls)),
)

client = Client()

class TestNodeTreeModelPermissions(TestCase):

    urls = 'nodetree.tests.permissions'

    def setUp(self):
        self.town = Town.objects.create(name='Zurich')
        self.town_node = Node.objects.create(node_type='town', content=self.town)

        self.area = Area.objects.create(name='Wiedikon')
        self.area_node = Node.objects.create(node_type='area', content=self.area, parent=self.town_node)

        self.house = House.objects.create(name='Kalkbreitestrasse 98')
        self.house_node = Node.objects.create(node_type='house', content=self.house, parent=self.area_node)

        self.user = User.objects.create_user('lukasbuenger', 'lukasbuenger@gmail.com', password='any-password')
        for code_name in ['add_node', 'add_town', 'change_node', 'change_town', 'add_person', 'change_person']:
            permission = Permission.objects.get(codename=code_name)
            self.user.user_permissions.add(permission)

        client.login(username='lukasbuenger', password='any-password')

    def test_post_list_permissions(self):
        response = client.post('/nodetree/node/', json.dumps({
            'node_type': 'town',
            'content': {
                'name': 'Berne',
            }
        }), content_type='application/json')
        self.assertEqual(response.status_code, 201)

    def test_not_provided_post_list_permissions(self):
        response = client.post('/nodetree/node/', json.dumps({
            'node_type': 'area',
            'content': {
                'name': 'Seefeld',
            }
        }), content_type='application/json')
        self.assertEqual(response.status_code, 403)

    def test_get_list_permissions(self):
        response = client.get('/nodetree/node/')
        self.assertEqual(response.status_code, 200)

    def test_invalid_put_detail_permission(self):
        response = client.put('/nodetree/node/3/', json.dumps({
            'target': '/nodetree/node/1/',
            'position': 'first-child',
        }), content_type='application/json')
        self.assertEqual(response.status_code, 403)