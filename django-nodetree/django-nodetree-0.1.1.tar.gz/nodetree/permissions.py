# -*- coding: utf-8 -*- 
from __future__ import unicode_literals

from rest_framework.permissions import DjangoModelPermissions

import nodetree


class NodePermissionMixin(object):

    def get_model_class(self, request, view):
        try:
            node_type = view.get_object().node_type
        except:
            node_type = request.DATA.get('node_type')
        if node_type is not None:
            node_type_obj = nodetree.app.get_node_type(node_type)
            if node_type_obj:
                return node_type_obj.model_class
        return None


class NodeTreeModelPermissions(NodePermissionMixin, DjangoModelPermissions):

    def has_permission(self, request, view):

        if not super(NodeTreeModelPermissions, self).has_permission(request, view):
            return False

        model_cls = self.get_model_class(request, view)
        if not model_cls:
            return True

        perms = self.get_required_permissions(request.method, model_cls)


        if (request.user and
            (request.user.is_authenticated() or not self.authenticated_users_only) and
            request.user.has_perms(perms)):
            return True
        return False