from __future__ import absolute_import

import pyprotobuf.nodes as nodes
from pyprotobuf.visitor import Visitor

class Frame(object):
    def __init__(self):
        self.ids = []
        self.id_scope = ['']

    def resolve_name(self, name):
        for scope in self.ids:
            if name in scope:
                return scope[name]
        raise Exception('Couldnt resolve %s' % name)
        
class CodeGenerator(Visitor):
    def push_frame(self, parent, frame):
        frame.ids.append({})
        #print 'PARENT %r' % parent
        # single pass to collect the ids
        for child in getattr(parent, 'children', []):
            if isinstance(child, (nodes.MessageNode, nodes.EnumNode)):
                if frame.id_scope[-1] != '':
                    fullname = child.name
                else:
                    fullname = '%s.%s' % (frame.id_scope[-1], child.name)
                frame.ids[-1][fullname] = child
                frame.ids[-1][child.name] = child
                
    def visit(self, parent, frame=None, out=None):
        if frame is None:
            frame = Frame()
           
        self.push_frame(parent, frame)
        children =getattr(parent, 'children', [])
        
        if out is None:
            out = []
            
        for child in children:
            cls = child.__class__.__name__
            if hasattr(self, 'visit_%s' % cls):

                out.insert(0, getattr(self, 'visit_%s' % cls)(child, frame))

            else:
                #print child
                self.visit_unknown(child, frame)
                #out.append()
                
            if getattr(child, 'children', []):
                frame.id_scope.append(child.name)
                self.visit(child, frame, out)
                frame.id_scope.pop()
                

        return ''.join(filter(lambda x: isinstance(x, basestring), out))
                
                
    def visit_unknown(self, child, frame):
        #raise Exception('Unknown something visited')
        #print 'unknown', child
        pass        
  
