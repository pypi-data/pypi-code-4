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
    
    def generate_file(self, protonode):
        self.output.write('/* Automatically generated. Do not modify this file.\n   %s\n*/\n' % protonode.filename)
        self.visit(protonode) 
        return self.output.to_string()
    
    def visit_OptionNode(self, node):
        """ Prefix the generated messages with javascript_package (if defined).

            XXX: just use the package statement?
        """
        if node.name == 'javascript_package':
            self.prefix = node.value.strip('"') + '.'

    def visit_MessageNode(self, node):
        fields = filter(lambda x: isinstance(x, nodes.FieldDescriptorNode), node.children)
        fields = sorted(fields, key=lambda x: x.number)

        messagemeta = {'name': node.name}

        self.output.write('\n\n/** @constructor */\n')
        self.output.write('%s%s = function(){};\n\n' % (self.prefix, node.name))
        
        for field in fields:

            if isinstance(field.type, nodes.MessageNode) or  isinstance(field.type, nodes.EnumNode):
                jstype = self.prefix + field.type.name
            else:
                jstype = JS_TYPE_MAP.get(field.type, None)
                
            if field.label == "repeated":
                jstype = '[%s]' % jstype
             
            self.output.write('/** @type {%s} */\n' % jstype)
            self.output.write('{0}{1}.prototype.{2};\n\n'.format(self.prefix, messagemeta['name'], field.name))                

                
    def visit_FieldDescriptorNode(self, node):
        pass
            
            
__generator__ = ClosureExterns
