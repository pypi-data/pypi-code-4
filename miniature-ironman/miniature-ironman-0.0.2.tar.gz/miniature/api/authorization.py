from tastypie.authorization import DjangoAuthorization
from tastypie.exceptions import Unauthorized

__author__ = 'ir4y'


class AuthorizationWithObjectPermissions(DjangoAuthorization):
        def create_list(self, object_list, bundle):
            klass = self.base_checks(bundle.request, object_list.model)

            if klass is False:
                return []

            permission = '%s.add_%s' % (klass._meta.app_label,
                                        klass._meta.module_name)

            if not bundle.request.user.has_perm(permission, object_list):
                return []

            return object_list

        def create_detail(self, object_list, bundle):
            klass = self.base_checks(bundle.request, bundle.obj.__class__)

            if klass is False:
                raise Unauthorized(
                    "You are not allowed to access that resource.")

            permission = '%s.add_%s' % (klass._meta.app_label,
                                        klass._meta.module_name)

            if not bundle.request.user.has_perm(permission):
                raise Unauthorized(
                    "You are not allowed to access that resource.")

            return True

        def update_list(self, object_list, bundle):
            klass = self.base_checks(bundle.request, object_list.model)

            if klass is False:
                return []

            permission = '%s.change_%s' % (klass._meta.app_label,
                                           klass._meta.module_name)

            if not bundle.request.user.has_perm(permission, object_list):
                return []

            return object_list

        def update_detail(self, object_list, bundle):
            klass = self.base_checks(bundle.request, bundle.obj.__class__)

            if klass is False:
                raise Unauthorized(
                    "You are not allowed to access that resource.")

            permission = '%s.change_%s' % (klass._meta.app_label,
                                           klass._meta.module_name)

            if not bundle.request.user.has_perm(permission, bundle.obj):
                raise Unauthorized(
                    "You are not allowed to access that resource.")

            return True

        def delete_list(self, object_list, bundle):
            klass = self.base_checks(bundle.request, object_list.model)

            if klass is False:
                return []

            permission = '%s.delete_%s' % (klass._meta.app_label,
                                           klass._meta.module_name)

            if not bundle.request.user.has_perm(permission, object_list):
                return []

            return object_list

        def delete_detail(self, object_list, bundle):
            klass = self.base_checks(bundle.request, bundle.obj.__class__)

            if klass is False:
                raise Unauthorized(
                    "You are not allowed to access that resource.")

            permission = '%s.delete_%s' % (klass._meta.app_label,
                                           klass._meta.module_name)

            if not bundle.request.user.has_perm(permission, bundle.obj):
                raise Unauthorized(
                    "You are not allowed to access that resource.")

            return True
