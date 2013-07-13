from __future__ import absolute_import

import pyprotobuf.nodes as nodes
from pyprotobuf.codegenerator import CodeGenerator

# javascript has small int types, represented as strings
JS_TYPE_MAP = {
    'bool':'boolean',
    'bytes': 'string',
    'double': 'number',    
    'fixed32': 'number',
    'fixed64': 'string', 
    'float': 'number', 
    'int32': 'number',
    'int64': 'string',        
    'sfixed32': 'number',    
    'sfixed64': 'string',   
    'sint32': 'number',
    'sint64': 'string', 
    'string': 'string',
    'uint32': 'number',
    'uint64': 'string', 
}

class ClosureExterns(CodeGenerator):
    comment = '//'
    prefix = ''
    
    def to_src(self, protonode):
        out = []
        out.append('/* Automatically generated. Do not modify this file.\n   %s\n*/\n' % protonode.filename)
        out.append(self.visit(protonode)) 
        return ''.join(out)
    
    def visit_OptionNode(self, node, frame):
        ''' Prefix the generated messages with javascript_package (if defined).
        '''
        if node.name == 'javascript_package':
            self.prefix = node.value.strip('"') + '.'

    def visit_MessageNode(self, node, frame):
        fields = filter(lambda x: isinstance(x, nodes.FieldDescriptorNode), node.children)
        fields = sorted(fields, key=lambda x: x.number)

        messagemeta = {'name': node.name}

        out = ['\n\n/** @constructor */\n']
        out.append('%s%s = function(){};\n\n' % (self.prefix, node.name))
        
        for field in fields:

            if isinstance(field.type, (nodes.MessageNode)) or  isinstance(field.type, nodes.EnumNode):
                jstype = self.prefix + field.type.name
            else:
                jstype = JS_TYPE_MAP.get(field.type, None)
                
            if field.label == "repeated":
                jstype = '[%s]' % (jstype)                
             
            out.append('/** @type {%s} */\n' % jstype)
            out.append('{0}{1}.prototype.{2};\n\n'.format(self.prefix, messagemeta['name'], field.name))                
        
        return ''.join(out)

                
    def visit_FieldDescriptorNode(self, node, frame):
        pass
            
            
__generator__ = ClosureExterns
