# -*- coding: utf-8 -*- 
from __future__ import unicode_literals

from django.core.exceptions import ObjectDoesNotExist
from django.http import Http404

from rest_framework.decorators import link
from rest_framework.generics import GenericAPIView
from rest_framework.mixins import RetrieveModelMixin, UpdateModelMixin, ListModelMixin
from rest_framework.permissions import SAFE_METHODS
from rest_framework.settings import api_settings
from rest_framework.viewsets import ModelViewSet, ViewSetMixin

import nodetree
from nodetree.exceptions import QueryParamError
from nodetree.filters import node_filter_set, node_filter_backend
from nodetree.models import Node
from nodetree.settings import nodetree_settings


class BaseContentViewSet(RetrieveModelMixin, UpdateModelMixin, ListModelMixin, ViewSetMixin, GenericAPIView):
    http_method_names = ['get', 'put', 'head', 'options']


class NodeViewSet(ModelViewSet):


    http_method_names = ['get', 'post', 'put', 'delete', 'head', 'options']
    permission_classes = nodetree_settings.NODE_PERMISSIONS or api_settings.DEFAULT_PERMISSION_CLASSES
    model = Node
    filter_set = node_filter_set
    filter_backend = node_filter_backend

    def get_depth(self):
        try:
            depth = self.request.QUERY_PARAMS.get('depth', nodetree_settings.DEFAULT_MAX_DEPTH)
            return int(depth)
        except ValueError:
            raise QueryParamError

    def get_serializer_class(self):
        if self.request.method in SAFE_METHODS or self.request.method == 'DELETE':
            return nodetree.app.get_node_serializer_class(self.get_depth())
        elif self.request.method == 'POST':
            return nodetree.app.get_create_node_serializer_class(self.get_depth())
        elif self.request.method in ['PUT', 'PATCH']:
            return nodetree.app.get_update_node_serializer_class(self.get_depth())


    def get_node(self, pk):
        try:
            node = Node.objects.get(pk=pk)
        except ObjectDoesNotExist:
            raise Http404
        return node

    @link()
    def ancestors(self, request, pk=None):
        self.queryset = self.get_node(pk).get_ancestors()
        return self.list(request)

    @link()
    def descendants(self, request, pk=None):
        self.queryset = self.get_node(pk).get_descendants()
        return self.list(request)

    @link()
    def children(self, request, pk=None):
        self.queryset = self.get_node(pk).get_children()
        return self.list(request)

    @link()
    def siblings(self, request, pk=None):
        self.queryset = self.get_node(pk).get_siblings()
        return self.list(request)

    @link()
    def root(self, request, pk=None):
        self.kwargs['pk'] = self.get_node(pk).get_root().pk
        return self.retrieve(request)
