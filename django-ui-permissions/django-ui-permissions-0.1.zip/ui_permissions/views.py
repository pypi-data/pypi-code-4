# -*- coding: utf-8 -*-

"""Module containing views mixins."""

from django.http import Http404
from django.core.urlresolvers import resolve


class UiPermViewMixin(object):

    """Base class for other view mixins."""

    def get_perm_desc(self, request, *args, **kwargs):
        """Get permissions class for given user in request.

        This method must be overridden. Returning None means that request for given URL(resource) is blocked.

        :param request: HTTP request
        :type request: django.http.HttpRequest
        :returns: class that inherits from ui_permissions.descriptor.permission.Permission or None
        :rtype: class or None

        """
        raise NotImplementedError()

    def dispatch(self, request, *args, **kwargs):
        permission_class = self.get_perm_desc(request, *args, **kwargs)
        if permission_class is None:
            raise Http404()

        resource_desc = permission_class.get_resource(resolve(request.path_info).url_name)
        if resource_desc is None:
            raise Http404()
        if not resource_desc.is_owner(request, kwargs):
            raise Http404()

        self.resource_desc = resource_desc()

        return super(UiPermViewMixin, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(UiPermViewMixin, self).get_context_data(**kwargs)
        context['resource_desc'] = self.resource_desc
        return context


class UiPermFormViewMixin(UiPermViewMixin):

    """Mixin used with Django built-in forms views."""

    def get_form_kwargs(self):
        kwargs = super(UiPermFormViewMixin, self).get_form_kwargs()
        kwargs['resource_desc'] = self.resource_desc
        return kwargs

