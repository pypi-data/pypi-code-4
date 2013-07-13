from __future__ import absolute_import
import logging
import pyprotobuf.nodes as nodes
from pyprotobuf.codegenerator import CodeGenerator
logger = logging.getLogger('pyprotobuf.nameresolve')

class NameResolveVisitor(CodeGenerator):
    ''' Parse the file looking to link together ParseNodes when they refer to each other.
    '''
    
    types = ['bool', 'string', 'int64', 'int32', 'uint64', 'uint32', 'sint64',
    'sint32', 'fixed64', 'fixed32', 'sfixed64', 'sfixed32', 'double', 'float',
    'bytes', 'enum', 'message', 'group']

    
    def visit_MessageNode(self, node, frame):
        # loop over fields
        fields = filter(lambda x: isinstance(x, nodes.FieldDescriptorNode), node.children)
        self.push_frame(node, frame)
        
        for field in fields:
            if field.type not in self.types:
                
                #if  field.type in frame.ids[-1]:
                #    reffield = frame.ids[-1][field.type]
                #    field.type = reffield
                #el
                if field.type == node.name:
                    logger.debug('Self reference %s <- %s.%s' % (node.name, node.name, field.name))
                    field.type = node
                else:
                    try:
                        # replace the field.type by searching the scopes
                        field.type = frame.resolve_name(field.type)
                    except Exception, e:
                        logger.error('%s',[repr(i) for i in frame.ids])
                        raise 
                        #raise Exception("Undefined reference %s" % field.type)
 
