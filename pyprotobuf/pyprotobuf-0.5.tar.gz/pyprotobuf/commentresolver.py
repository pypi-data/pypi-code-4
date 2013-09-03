from pyprotobuf.codegenerator import CodeGenerator

class CommentResolver(CodeGenerator):
    ''' associate comments with suceeding nodes 
    '''
    def __init__(self, frame=None):
        super(CommentResolver, self).__init__(frame)
        self.last_comment = None

    def visit(self, parent):
        for child in getattr(parent, 'children', []):
            cls = child.__class__.__name__
            if hasattr(self, 'visit_%s' % cls):
                getattr(self, 'visit_%s' % cls)(child)
            else:
                child.comment = self.last_comment
                self.last_comment = None
            self.visit(child)
    
    def visit_CommentNode(self, child):
        self.last_comment = child
        
        
    def visit_unknown(self, child):
        print 'unknown', child
