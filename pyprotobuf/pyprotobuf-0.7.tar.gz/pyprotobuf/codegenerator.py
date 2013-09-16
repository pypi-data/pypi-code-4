from __future__ import absolute_import
import logging
import pyprotobuf.nodes as nodes
from pyprotobuf.visitor import Visitor
from pyprotobuf.outputbuffer import OutputBuffer

logger = logging.getLogger("pyprotobuf.Frame")


class Frame(object):
    def __init__(self):
        self.ids = [{}]
        self.id_scope = ['']
        self.global_scope = [{}]
        self.local_scope = [{}]

    def resolve_name(self, name):
        assert isinstance(name, basestring)
        
        if isinstance(name, nodes.ParseNode):
            return name
        
        if name.find('.') == -1:
            for scope in self.local_scope:
                if name in scope:
                    return scope[name]
        else:
            for scope in self.global_scope:
                if name in scope:
                    return scope[name]
                
        raise Exception('Couldnt resolve %s: %s' % (name, self.global_scope))

    def add_to_globals(self, name, node):
        self.global_scope[-1][name] = node


    def add_to_locals(self, name, node):
        self.local_scope[-1][name] = node

    def add_node(self, node):
        
        #for child in getattr(node, 'children', []):
        if not isinstance(node, (nodes.MessageNode, nodes.EnumNode)):
            return
        

        
        if self.id_scope[-1] == '':
            fullname = node.name
        else:
            fullname = '%s.%s' % (self.id_scope[-1], node.name)

        logger.debug('Add node: %s (%s)', fullname, node.__class__.__name__)

        
        self.global_scope[-1][fullname] = node
        self.local_scope[-1][node.name] = node
        
        #logger.debug('Current ids:%s ', self.global_scope[-1].keys())
        
    def push_local_scope(self):
        self.local_scope.append({})
        
    def pop_local_scope(self):
        return self.local_scope.pop()
        
    def push_id_scope(self, prefix):
        logger.debug('Push scope %s', prefix)
        self.id_scope.append(prefix)

    def pop_id_scope(self):
        logger.debug('Pop scope %s', self.id_scope.pop())


class CodeGenerator(Visitor):
    logger = logging.getLogger("pyprotobuf.CodeGenerator")
    
    def __init__(self, frame=None):
        super(CodeGenerator, self).__init__()
        self.output = OutputBuffer()
        self.frame = frame or Frame()

    def visit_Package(self, package):
        """ Push the package name as the scope prefix. 
        """

        if package.is_named():
            self.frame.push_id_scope(package.name)

        self.logger.info('Visiting package node %s', package.name)

        self.visit(package)

        if package.is_named():
            self.frame.pop_id_scope()


    def visit(self, parent):

        self.frame.add_node(parent)

        children = getattr(parent, 'children', [])

        for child in children:
            cls = child.__class__.__name__

            # if defined, call the named visit_* function in subclasses
            if hasattr(self, 'visit_%s' % cls):
                getattr(self, 'visit_%s' % cls)(child)
            else:
                self.visit_unknown(child)

            # recurse into the children    
            if getattr(child, 'children', []):    
                self.visit(child)
                


    def visit_unknown(self, child):
        #raise Exception('Unknown something visited')
        #print 'unknown', child
        pass


    def generate_file(self, filenode):
        """ Generate  a FileNode.
         
        """
        raise NotImplementedError