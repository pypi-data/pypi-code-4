from __future__ import absolute_import
import json
import pyprotobuf.nodes as nodes
from pyprotobuf.codegenerator import CodeGenerator

PROTORPC_TYPE_MAP = {
    'bool':'messages.BooleanField',
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
    
    def to_src(self, protonode):
        out = [IMPORTS % protonode.filename + '\n\n']
        out.append(self.visit(protonode))        
        return ''.join(out)            
    
   
    def visit_MessageNode(self, node, frame, out=None, indent=0):
        # loop over fields
        fields = filter(lambda x: isinstance(x, nodes.FieldDescriptorNode), node.children)
        childmessages = filter(lambda x: isinstance(x, nodes.MessageNode), node.children)
        fields = sorted(fields, key=lambda x: x.number)
        all_field_meta = {}
        messagemeta = {'name': node.name}
        INDENT = '    ' *indent
        if out is None:
            out = []
        out.append(INDENT)
        
        out.append('class %(name)s(messages.Message):\n'% messagemeta)
        
        if node.comment:
            out.append("%s''' %s '''\n" % ('    ' *(indent+1), node.comment.value))
            
        lines = []
        
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
            
            INDENT = '    ' *(indent+1)
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
                field_meta['defaultValue'] = field.default
                line.append(", default=%(defaultValue)s" % field_meta)
            line.append(")")
            lines.append(''.join(line))
        
        out.append('\n'.join(lines))
        out.append('\n')
        
        if childmessages:
             out.append('\n')
             
        for childmessage in childmessages:
            self.visit_MessageNode(childmessage, frame, out, indent+1)
            
        
        out.append('\n\n')
        return  ''.join(out)
        
    def visit_FieldDescriptorNode(self, node, frame):
        pass
    
__generator__ = ProtoRPC
