from copy import deepcopy
from django.core.exceptions import ValidationError
from django.db.models import ForeignKey

from django.utils.safestring import mark_safe
from django_helpers.apps.static_manager.utils import get_js_files

from js_imports import require
from django_helpers.helpers.views import render_json


__author__ = 'ajumell'


def _error(content):
    return render_json({
        'err': True,
        'msg': str(content)
    })


def _success(content):
    return render_json({
        'err': False,
        'msg': content
    })


class XEditableMeta(type):
    def __new__(mcs, name, bases, attrs):
        from fields import BaseEditable

        new_class = type.__new__(mcs, name, bases, attrs)

        # This can be done now. Now think about a better syntax.
        fields = []
        field_names = []
        for attr_name, attr in attrs.iteritems():
            if isinstance(attr, BaseEditable):
                attr.field_name = attr_name

                if hasattr(new_class, attr_name):
                    delattr(new_class, attr_name)

                fields.append(attr)
                field_names.append(attr_name)

        new_class._fields = fields
        new_class._field_names = field_names

        return new_class


class XEditable(object):
    __metaclass__ = XEditableMeta

    has_js = True
    model = None
    _fields = None
    editable_id = None

    def __init__(self, instance=None, pk=None, is_ajax=False):
        if self.editable_id is None:
            raise

        self.is_ajax = is_ajax
        model = self.model
        if instance is not None:
            if not isinstance(instance, model):
                raise
            self.instance = instance
            self.pk = instance.pk
        else:
            self.instance = None
            self.pk = pk

        fields = self._fields
        new_fields = {}
        for field in fields:
            new_field = deepcopy(field)
            field_name = new_field.field_name
            new_field.editable = self
            new_field._load_validations_from_model()

            new_fields[field_name] = new_field
            setattr(self, field_name, new_field)

        self._fields = new_fields

    def get_instance(self):
        """
        @return: the current instance of the object.
        """
        instance = self.instance
        if instance is None:
            pk = self.pk
            if pk is None:
                raise
            instance = self.model.objects.get(pk=pk)
            self.instance = instance
        return instance

    def get_model_field_type(self, name):
        """
        @param name: name of the field
        @return: the value returned by the get_internal_type
        function of the model field.
        """
        cache_name = '_model_field_type_cache'
        if not hasattr(self, cache_name):
            setattr(self, cache_name, {})

        cache = getattr(self, cache_name)
        if name not in cache:
            field = self.get_model_field(name)
            val = field.get_internal_type()
            cache[name] = val
        else:
            val = cache[name]
        return val

    def get_model_field(self, name):
        """
        @param name: name of the field
        @return: returns the corresponding model field.
        """
        cache_name = '_model_field_cache'
        if not hasattr(self, cache_name):
            setattr(self, cache_name, {})

        cache = getattr(self, cache_name)
        if name not in cache:
            model = self.model
            val = model._meta.get_field_by_name(name)[0]
            cache[name] = val
        else:
            val = cache[name]
        return val

    def get_id(self, name):
        """
        @param name: name of the field
        @return: the auto-generated id for the field.
        """
        return "%s-%s-%s" % (self.editable_id, name, self.pk)

    def get_value(self, name):
        """
        @param name: name of the field
        @return: the python object of the field from the model instance
        """
        instance = self.get_instance()
        return getattr(instance, name, None)

    def validate(self, name, value):
        """
        Performs some basic validations. If a custom validation function
        is created for a field then it will be called.

        @param name: name of the field.
        @param value: the current python object for the field.
        @return: the cleaned value.
        """
        custom_validator = getattr(self, '%s_clean' % name, None)
        if hasattr(custom_validator, '__call__'):
            custom_validator()
        model_field = self.get_model_field(name)
        instance = self.get_instance()
        try:
            if isinstance(model_field, ForeignKey):
                _value = value.pk
            else:
                _value = value
            model_field.validate(_value, instance)
        except ValidationError, dt:
            raise Exception(', '.join(dt.messages))

        return value

    def render_field(self, name):
        field = self._fields[name]
        return field.render()

    def render_js(self):
        content = ''
        fields = self._fields
        for field_name in fields:
            field = fields[field_name]
            if field.has_rendered:
                js = field.render_js()
                if js is not None:
                    content += js
        return mark_safe(content)

    # View Functions

    def list(self, name):
        field = self._fields.get(name, None)
        if field is None:
            return _error('Server Error : Field does not exists.')
        return render_json(field.list())

    def save(self, request, name):
        field = self._fields.get(name, None)
        is_multivalued = getattr(field, 'is_multivalued', False)

        if field is None:
            return _error('Server Error : Field does not exists.')

        if is_multivalued:
            value = request.POST.getlist('value')
        else:
            value = request.POST.get('value')

        if value is None:
            # If no value came from request
            return _error('Server error : Value is None.')

        try:
            value = field.to_python(value)
            value = self.validate(name, value)
            instance = self.get_instance()
            setattr(instance, name, value)
            instance.clean()
            instance.save()
            op = field.to_string(value)
        except Exception, dt:
            return _error(dt)

        return _success(op)

    def js_files(self):
        files = require()
        fields = self._fields
        for field_name in fields:
            field = fields[field_name]
            files += get_js_files(field)
        return files