
class Visitor(object):
    def visit(self, parent):
        for child in getattr(parent, 'children', []):
            cls = child.__class__.__name__
            if hasattr(self, 'visit_%s' % cls):
                getattr(self, 'visit_%s' % cls)(child)
            else:
                self.visit_unknown(child)
            self.visit(child)
            
    def visit_unknown(self, child):
        print 'unknown', child
