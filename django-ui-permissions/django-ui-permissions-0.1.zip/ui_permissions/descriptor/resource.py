# -*- coding: utf-8 -*-

"""Module containing element used for describing permissions to given resources."""

import copy

from ui_permissions.descriptor.components.base import Component
from ui_permissions.descriptor.components import Field, Element


def add_component_type_property(instance, component_type_name, components, component_cls=None):
    """Adds property that contains components filtered by type.

    :param instance: resource instance
    :type instance: ui_permissions.descriptor.resource.Resource
    :param component_type_name: name of the component type property that will by attached to instance
    :type component_type_name: str
    :param components: components that will be stored under component type property
    :type components: dict
    :param component_cls: class of the given component
    :type component_cls: type

    """
    default_state_id = instance._Settings.default_if_not_present[component_type_name]
    component_type_property = ResourceWrapper(components, default_state_id, component_cls)
    setattr(instance, component_type_name, component_type_property)


class Resource(object):

    """Precise resource permission description."""

    def __new__(cls):
        instance = super(Resource, cls).__new__(cls)
        components_dict = {}
        for attr_name in dir(instance):
            attr = getattr(instance, attr_name)
            if isinstance(attr, Component):
                component_type_name = type(attr).__name__.lower()
                if component_type_name not in components_dict:
                    components_dict[component_type_name] = {}
                components_dict[component_type_name][attr_name] = copy.deepcopy(attr)
        for type_name, components in components_dict.items():
            add_component_type_property(instance, type_name, components)

        if 'field' not in components_dict:
            add_component_type_property(instance, 'field', {}, Field)
        if 'element' not in components_dict:
            add_component_type_property(instance, 'element', {}, Element)

        return instance

    @classmethod
    def is_owner(cls, request, view_kwargs):
        """Checks if user is allowed to see resource.

        :param request: url name
        :type request: HttpRequest
        :param view_kwargs: keyword arguments passed to view
        :type view_kwargs: dict
        :returns: True if user is allowed to see the resource
        :rtype: bool

        """
        return True

    def get_excluded_fields(self, additional_fields=None):
        """Make list of all Fields that are not allowed to be edited by user.

        :param additional_fields: additional fields to check
        :type additional_fields: list
        :returns: list of field names
        :rtype: list

        """
        if additional_fields is None:
            additional_fields = []

        additional_fields = self._get_undefined_fields(additional_fields)
        excluded_fields = []

        for name, value in self.__class__.__dict__.items():
            if isinstance(value, Field) and value.exclude:
                excluded_fields.append(name)

        if self._Settings.default_if_not_present['field'] in Field.excluding_states():
            excluded_fields.extend(additional_fields)

        return excluded_fields

    def _get_undefined_fields(self, fields):
        """Get names of fields from given list that are not defined in resource description class.

        :param fields: list of field names
        :type fields: list
        :returns: list of undefined field names
        :rtype: list

        """
        undefined_fields = []
        for field_name in fields:
            if not hasattr(self, field_name):
                undefined_fields.append(field_name)
        return undefined_fields

    class _Settings:
        url = []
        default_if_not_present = {'field': Field.EDITABLE,
                                  'element': Element.VISIBLE}


class ResourceWrapper(object):

    """Helper class for accessing filtered components."""

    def __init__(self, components, default_state_id, component_cls=None):
        self._components = components
        self._component_cls = type(components.values()[0]) if component_cls is None else component_cls
        self._default_state_id = default_state_id

    def __getattr__(self, name):
        return ComponentWrapper(self._components.get(name, self._component_cls), self._default_state_id)


class ComponentWrapper(object):

    """Helper class for checking component state."""

    def __init__(self, component, default_state_id):
        self._component = component
        self._default_state_id = default_state_id

    def __getattr__(self, name):
        if not hasattr(self._component, name):
            raise AttributeError(name)
        if isinstance(self._component, Component):
            state_value = self._component.state_id
        else:
            state_value = self._default_state_id
        return getattr(self._component, name) == state_value


class _base_settings_decorator(object):

    """Base settings decorator."""

    def _fabricate_settings(self, decorated_class):
        """Creates new settings class.

        :param decorated_class: decorated class
        :type decorated_class: Resource type class
        :returns: new settings class
        :rtype: Resource._Settings

        """
        class NewSettings:
            url = copy.deepcopy(decorated_class._Settings.url)
            default_if_not_present = copy.deepcopy(decorated_class._Settings.default_if_not_present)

        decorated_class._Settings = NewSettings


class url(_base_settings_decorator):

    """Sets allowed URL-s."""

    def __init__(self, *url_names):
        self.url_names = url_names

    def __call__(self, cls):
        self._fabricate_settings(cls)
        cls._Settings.url = self.url_names
        return cls


class default_if_not_present(_base_settings_decorator):

    """Sets default value for resource description if not present in Resource class definition."""

    def __init__(self, **defaults):
        for default_name in defaults.keys():
            if default_name not in Resource._Settings.default_if_not_present.keys():
                raise AttributeError(u"'%s' is not allowed parameter" % default_name)
        self.defaults = defaults

    def __call__(self, cls):
        self._fabricate_settings(cls)
        cls._Settings.default_if_not_present.update(self.defaults)
        return cls
