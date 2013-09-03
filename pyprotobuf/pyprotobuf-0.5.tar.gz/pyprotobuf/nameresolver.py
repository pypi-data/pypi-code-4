from __future__ import absolute_import
import logging
import pyprotobuf.nodes as nodes
from pyprotobuf.codegenerator import CodeGenerator


class NameResolver(CodeGenerator):
    ''' Parse the file looking to link together ParseNodes when they refer to each other.
    '''
    
    types = ['bool', 'string', 'int64', 'int32', 'uint64', 'uint32', 'sint64',
    'sint32', 'fixed64', 'fixed32', 'sfixed64', 'sfixed32', 'double', 'float',
    'bytes', 'enum', 'message', 'group']

    logger = logging.getLogger('pyprotobuf.NameResolver')
    
    def visit_MessageNode(self, node):
        self.logger.debug('Visit message %s', node.name)

        frame = self.frame
        fields = node.get_children_of_type(nodes.FieldDescriptorNode)
        
        for field in fields:
            # only handle special types
            if field.type in self.types:
                continue
                
            
            if field.type == node.name:
                self.logger.debug('Self reference %s <- %s.%s' % (node.name, node.name, field.name))
                field.type = node
                continue
                
            # only evaluate non evaluated
            if not isinstance(field.type, nodes.ParseNode):
                try:
                    # replace the field.type by searching the scopes
                    field.type = frame.resolve_name(field.type)
                except Exception, e:
                    self.logger.error('%s',[repr(i) for i in frame.ids])
                    raise 
                    #raise Exception("Undefined reference %s" % field.type)
            
            

