from __future__ import absolute_import
import logging
import pyprotobuf.nodes as nodes
from pyprotobuf.codegenerator import CodeGenerator

logger = logging.getLogger('pyprotobuf.protorpc')

PROTORPC_TYPE_MAP = {
    'bool': 'messages.BooleanField',
    'bytes': 'messages.BytesField',
    'double': 'messages.FloatField',
    'enum': 'messages.EnumField',
    'fixed32': 'messages.IntegerField',
    'fixed64': 'messages.IntegerField',
    'float': 'messages.FloatField',
    'int32': 'messages.IntegerField',
    'int64': 'messages.IntegerField',
    'message': 'messages.MessageField',
    'sfixed32': 'messages.IntegerField',
    'sfixed64': 'messages.IntegerField',
    'sint32': 'messages.IntegerField',
    'sint64': 'messages.IntegerField',
    'string': 'messages.StringField',
    'uint32': 'messages.IntegerField',
    'uint64': 'messages.IntegerField',
}

IMPORTS = '''################################################################################
# Automatically generated. Do not modify this file                             #
################################################################################
# %s

from protorpc import messages
'''


class ProtoRPC(CodeGenerator):
    comment = '#'

    def generate_file(self, protonode):
        self.output.write(IMPORTS % protonode.filename + '\n\n')
        self.visit(protonode)
        return self.output.to_string()

    def visit_EnumNode(self, node, indent=0):

        if getattr(node, 'visited', False):
            return

        INDENT = '    ' * indent

        self.output.write(INDENT)
        self.output.write('class %s(messages.Enum):\n' % node.name)

        enum_assignments = filter(lambda x: isinstance(x, nodes.EnumAssignmentNode), node.children)

        INDENT = '    ' * (indent + 1)
        for enum in enum_assignments:
            name, value = enum.name, enum.value
            self.output.write(INDENT)
            self.output.write("%s = %s\n" % (name, value))

        self.output.write('\n')

        # mark as visited so we dont output twice
        # XXX: improve file node traversal so we dont need this
        setattr(node, 'visited', True)


    def visit_MessageNode(self, node, indent=0):
        # loop over fields

        enums = filter(lambda x: isinstance(x, nodes.EnumNode), node.children)
        fields = filter(lambda x: isinstance(x, nodes.FieldDescriptorNode), node.children)
        childmessages = filter(lambda x: isinstance(x, nodes.MessageNode), node.children)
        fields = sorted(fields, key=lambda x: x.number)
        all_field_meta = {}
        messagemeta = {'name': node.name}
        INDENT = '    ' * indent

        self.output.write(INDENT)

        self.output.write('class %(name)s(messages.Message):\n' % messagemeta)

        if node.comment:
            self.output.write("%s''' %s '''\n" % ('    ' * (indent + 1), node.comment.value))

        lines = []

        for enum in enums:
            self.visit_EnumNode(enum, indent+1)

        for field in fields:
            field_number = field.number
            field_meta = all_field_meta[field_number] = {}

            fieldtype = PROTORPC_TYPE_MAP.get(field.type)

            field_meta['type'] = ''

            name = field.name
            if isinstance(field.type, nodes.MessageNode):
                field_meta['type'] = '"%s"' % field.type.name + ', '
                fieldtype = 'messages.MessageField'
            elif isinstance(field.type, nodes.EnumNode):
                fieldtype = PROTORPC_TYPE_MAP.get('enum')

            field_meta['number'] = field.number
            field_meta['name'] = name
            field_meta['fieldType'] = fieldtype

            INDENT = '    ' * (indent + 1)
            line = []

            if field.comment:
                line.append("%s''' %s '''\n" % (INDENT, field.comment.value))

            line.append(INDENT)
            line.append("%(name)s = %(fieldType)s(%(type)s%(number)s" % field_meta)

            if field.label == "required":
                field_meta['required'] = True
                line.append(", required=True")

            if field.label == "repeated":
                field_meta['repeated'] = True
                line.append(", repeated=True")

            if hasattr(field, 'default'):
                if hasattr(field, 'default_node'):
                    enum_node = field.default_node
                    #field_meta['defaultValue'] = field.default

                    # build a FQN up to this message node
                    fqn = [enum_node.name]
                    for parent in enum_node.get_parents():
                        if parent == node:
                            break
                        if parent.name is None:
                            break
                        fqn.append(parent.name)

                    logger.debug('Generate enum %s', fqn)
                    fqn = '.'.join(reversed(fqn))

                    field_meta['defaultValue'] = '%s' % fqn
                else:
                    field_meta['defaultValue'] = field.default

                line.append(", default=%(defaultValue)s" % field_meta)

            line.append(")")
            lines.append(''.join(line))

        self.output.write('\n'.join(lines))
        self.output.write('\n')

        if childmessages:
            self.output.write('\n')

        for childmessage in childmessages:
            self.visit_MessageNode(childmessage, indent + 1)

        self.output.write('\n\n')

    def visit_FieldDescriptorNode(self, node):
        pass


__generator__ = ProtoRPC
