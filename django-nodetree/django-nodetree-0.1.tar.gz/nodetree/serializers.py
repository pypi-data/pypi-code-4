# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _

from rest_framework import serializers

import nodetree
from nodetree.models import Node
from nodetree.settings import nodetree_settings


class BaseContentSerializer(serializers.HyperlinkedModelSerializer):

    node = serializers.HyperlinkedRelatedField(view_name='node-detail', read_only=True)

    class Meta:
        exclude = ('id', )


class BaseNodeSerializer(serializers.HyperlinkedModelSerializer):

    parent = serializers.HyperlinkedRelatedField(view_name='node-detail')

    class Meta:
        model = Node
        exclude = ('content_type', 'object_id', 'id', 'lft', 'rght', 'tree_id', )


class BaseInputNodeSerializer(serializers.Serializer):

    max_depth = None

    target = serializers.HyperlinkedRelatedField(view_name='node-detail', queryset=Node.objects.all(), required=False)
    position = serializers.ChoiceField(choices=(
            ('first-child', _('First child')),
            ('last-child', _('Last child')),
            ('left', _('Left')),
            ('right', _('Right')),
        ), required=False)

    nodetree_error_messages = {
        'invalid_root': _("Node type '%s' can't be used as root." ),
        'position_required': _("You have to provide a 'position' in combination with a 'target'." ),
        'invalid_child': _("You can't add node type '%s' as child of '%s'." ),
        'invalid_node_type': _("Node type '%s' does not exist." ),
        'invalid_target': _("You can't use the object you want to move as target." ),
    }

    def __init__(self, *args, **kwargs):
        if self.max_depth is None:
            self.max_depth = nodetree_settings.DEFAULT_MAX_DEPTH
        super(BaseInputNodeSerializer, self).__init__(error_messages=self.nodetree_error_messages, *args, **kwargs)

    def get_parent(self, target, position):

        if position in ('left', 'right'):
            return target.parent
        else:
            return target

    def get_node_type(self, node_type):
        return nodetree.app.get_node_type(node_type)

    def has_node_type(self, node_type):
        return nodetree.app.has_node_type(node_type)

    def get_output_serializer(self):
        return nodetree.app.get_node_serializer_class(depth=self.max_depth)

    def validate(self, attrs):
        node_type = attrs.get('node_type')
        target = attrs.get('target', None)
        position = attrs.get('position', None)
        node_type_obj = self.get_node_type(node_type)

        if target is None:
            if node_type_obj.is_root is not True:
                raise ValidationError(self.error_messages['invalid_root'] % node_type_obj.name)
            return attrs
        else:
            if position is None:
                raise ValidationError(self.error_messages['position_required'])
            parent = self.get_parent(target, position)
            if parent is None and node_type_obj.is_root is not True:
                raise ValidationError(self.error_messages['invalid_root'] % node_type_obj.name)
            parent_node_type_obj = self.get_node_type(parent.node_type)
            if not parent_node_type_obj.is_allowed_child(node_type_obj.name):
                raise ValidationError(self.error_messages['invalid_child'] % (node_type_obj.name, parent_node_type_obj.name))

        return attrs

    def restore_object(self, attrs, instance=None):
        if instance is not None:
            Node.objects.move_node(instance, attrs.get('target'), attrs.get('position'))
        else:
            node_type_obj = self.get_node_type(attrs.get('node_type'))
            content = attrs.get('content')
            content.save()
            instance = Node(node_type=node_type_obj.name, content=content)
            Node.objects.insert_node(instance, attrs.get('target'), attrs.get('position'))
        return instance

    @property
    def data(self):
        if not self.object:
            raise Exception("You can't call the 'data' attribute of a 'BaseNodeInputSerializer' that doesn't represent "
                            "an existing 'Node' object.")
        return self.get_output_serializer()(self.object, context=self.context).data


class BaseUpdateNodeSerializer(BaseInputNodeSerializer):

    def validate(self, attrs):
        if attrs['target'] == self.object:
            raise ValidationError(self.error_messages['invalid_target'])
        attrs['node_type'] = self.object.node_type
        attrs = super(BaseUpdateNodeSerializer, self).validate(attrs)
        parent = self.get_parent(attrs['target'], attrs['position'])
        if parent is not None and parent == self.object:
            raise ValidationError(self.error_messages['invalid_target'])
        return attrs


class BaseCreateNodeSerializer(BaseInputNodeSerializer):

    node_type = serializers.SlugField(max_length=31)

    def validate_node_type(self, attrs, source):

        node_type = attrs[source]
        if not self.has_node_type(node_type):
            raise ValidationError(self.error_messages['invalid_node_type'] % node_type)
        return attrs