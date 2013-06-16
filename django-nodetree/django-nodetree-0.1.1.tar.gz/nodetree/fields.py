# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import inspect

from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.core.urlresolvers import get_script_prefix, resolve
from django.utils.translation import ugettext_lazy as _
from django import forms

from rest_framework.compat import  urlparse
from rest_framework import six
from rest_framework import serializers
from rest_framework.exceptions import ConfigurationError
from rest_framework.relations import RelatedField
from rest_framework.serializers import NestedValidationError

import nodetree


class GenericRelatedField(serializers.WritableField):
    """
    Represents a generic relation foreign key.
    It's actually more of a wrapper, that delegates the logic to registered serializers based on the `Model` class.
    """
    default_error_messages = {
        'no_model_match': _('Invalid model - model not available.'),
        'no_url_match': _('Invalid hyperlink - No URL match'),
        'incorrect_url_match': _('Invalid hyperlink - view name not available'),
    }

    form_field_class = forms.URLField

    def __init__(self, serializers, *args, **kwargs):
        """
        Needs an extra parameter `serializers` which has to be a dict key: value being `Model`: serializer.
        """
        super(GenericRelatedField, self).__init__(*args, **kwargs)
        self.serializers = serializers
        for model, serializer in six.iteritems(self.serializers):
            # We have to do it, because the serializer can't access a explicit manager through the
            # GenericForeignKey field on the model.
            if hasattr(serializer, 'queryset') and serializer.queryset is None:
                serializer.queryset = model._default_manager.all()

    def field_to_native(self, obj, field_name):
        """
        Delegates to the `to_native` method of the serializer registered under obj.__class__
        """
        value = super(GenericRelatedField, self).field_to_native(obj, field_name)
        serializer = self.determine_deserializer_for_data(value)

        # Necessary because of context, field resolving etc.
        serializer.initialize(self.parent, field_name)
        return serializer.to_native(value)

    def to_native(self, value):
        # Override to prevent the simplifying process of value as present in `WritableField.to_native`.
        return value

    def from_native(self, value):
        # Get the serializer responsible for input resolving
        serializer = self.determine_serializer_for_data(value)
        serializer.initialize(self.parent, self.source)
        args = [value]
        if len(inspect.getargspec(serializer.from_native).args) > 2:
            args.append(None)
        return serializer.from_native(*args)

    def determine_deserializer_for_data(self, value):
        try:
            model = value.__class__
            serializer = self.serializers[model]
        except KeyError:
            raise ValidationError(self.error_messages['no_model_match'])
        return serializer

    def determine_serializer_for_data(self, value):
        for serializer in six.itervalues(self.serializers):
            if not isinstance(serializer, serializers.HyperlinkedRelatedField):
                raise ConfigurationError('Please use HyperlinkedRelatedField as serializers on GenericRelatedField \
                instances with read_only=False or set read_only=True.')

        # This excerpt is an exact copy of ``rest_framework.relations.HyperlinkedRelatedField``, Line 363
        # From here until ...
        try:
           http_prefix = value.startswith('http:') or value.startswith('https:')
        except AttributeError:
           msg = self.error_messages['incorrect_type']
           raise ValidationError(msg % type(value).__name__)

        if http_prefix:
            # If needed convert absolute URLs to relative path
            value = urlparse.urlparse(value).path
            prefix = get_script_prefix()
            if value.startswith(prefix):
                value = '/' + value[len(prefix):]
        try:
            match = resolve(value)
        except Exception:
            raise ValidationError(self.error_messages['no_url_match'])

        # ... here

        matched_serializer = None
        for serializer in six.itervalues(self.serializers):
            if serializer.view_name == match.url_name:
                matched_serializer = serializer

        if matched_serializer is None:
            raise ValidationError(self.error_messages['incorrect_url_match'])
        return matched_serializer


class RecursiveRelatedField(RelatedField):

    def __init__(self, max_depth=-1, leaf_serializer=None, *args, **kwargs):
        super(RecursiveRelatedField, self).__init__(*args, **kwargs)
        # Forced read only.
        self.max_depth = max_depth
        self.leaf_serializer = leaf_serializer
        self.read_only = True

    def field_to_native(self, obj, field_name):

        serializer_class = self.parent.__class__
        serializer = serializer_class()
        serializer.initialize(self.parent, field_name)


        if self.max_depth > -1:
            # We decrease max_depth here
            if self.max_depth > 0:
                serializer.fields[field_name].max_depth = self.max_depth - 1
            else:
                # Here's the handling of the leaf case if no leaf serializer is given.
                if self.leaf_serializer is None:
                    return [] if self.many else None
                elif not self.many:
                    # Here's the handling of the leaf case if a leaf serializer is given and `many` is set to `False`.
                    self.leaf_serializer.initialize(self.parent, field_name)
                    return self.leaf_serializer.to_native(getattr(obj, self.source or field_name))

        if self.many:
            related_manager = getattr(obj, self.source or field_name)
            if not obj.__class__ == related_manager.model:
                raise Exception('`RecursiveRelatedField` must point at a self-referencing relation.')
            queryset = related_manager.all()
            if not self.max_depth == 0:
                return [serializer.to_native(item) for item in queryset]
            else:
                self.leaf_serializer.initialize(self.parent, field_name)
                return [self.leaf_serializer.to_native(item) for item in queryset]

        try:
            queryset = getattr(obj, self.source or field_name)
            if not obj.__class__ == queryset.__class__:
                raise Exception('`RecursiveRelatedField` must point at a self-referencing relation.')
        except ObjectDoesNotExist:
            return None
        return serializer.to_native(queryset)

    def to_native(self, value):
        # Override to prevent simplifying process as present in `WritableField`.
        return value


class ContentField(GenericRelatedField):

    nodetree_error_messages = {
        'no_node_type_match': _('Invalid node type - model not available.'),
    }

    def __init__(self, *args, **kwargs):
        super(ContentField, self).__init__(error_messages=self.nodetree_error_messages, *args, **kwargs)

    def determine_serializer_for_data(self, value):

        node_type = self.parent.init_data.get('node_type', None)
        node_type_obj = nodetree.app.get_node_type(node_type)

        if node_type_obj is None:
            raise ValidationError(self.error_messages['no_node_type_match'])
        return node_type_obj.serializer_class()

    def from_native(self, value):
        # Get the serializer responsible for input resolving
        serializer = self.determine_serializer_for_data(value)
        serializer.initialize(self.parent, self.source)
        args = [value]
        if len(inspect.getargspec(serializer.from_native).args) > 2:
            args.append(None)
        result = serializer.from_native(*args)
        if not result:
            raise NestedValidationError(serializer.errors)
        return result