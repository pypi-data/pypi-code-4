class ParseNode(object):
    children = None
    comment = None
    
    def __init__(self, parent=None):
        self.children= []
        self.parent = parent
        self.name = None
        self.type = None
        self.comment = None
        
    def add_child(self, c):
        assert isinstance(c, ParseNode), "Child must be a ParseNode. Got %s" % type(c)
        self.children.append(c)
        
    def get_child(self, index):
        return self.children[index]
        
    def get_full_typename(self):
        fqn = [self.type.name]
        parent = self.parent
        while parent is not None:
            if parent.name is not None:
                fqn.append(parent.name)
            parent = parent.parent
            
        return '.'.join(list(reversed(fqn)))
        
    def get_full_name(self):
        fqn = [self.name]
        parent = self.parent
        while parent is not None:
            if parent.name is not None:
                fqn.append(parent.name)
            parent = parent.parent
            
        return '.'.join(list(reversed(fqn)))
        
    def __repr__(self):
        return '%s(%s, %s, [%s], %s)' % (self.__class__.__name__, self.name, self.type, ','.join([repr(f) for f in self.children]), self.comment)
            
class ProtoNode(ParseNode):
    pass

class CommentNode(ParseNode):
    pass

class PackageNode(ParseNode):
    name = None
    def __str__(self):
        return 'package %s;' % self.name
        
class ServiceNode(ParseNode):
    name = None
    def __str__(self):
        string = []
        for child in self.children:
            if isinstance(child, MessageNode):
                string.append(child.tostr(1))
            else:
                string.append(str(child))
                
        string = '\n'.join([('   ' +f) for f in string])
        return "service %s {\n%s\n%s}" % (self.name, string, '   ')
        
class MethodNode(ParseNode):
    name = None
    request_type = None
    response_type = None
    def __str__(self):
        return "rpc %s (%s) returns (%s);" % (self.name, self.request_type, self.response_type)
        
        
class MessageNode(ParseNode):
    name = None
    def tostr(self, depth):
        string = []
        for child in self.children:
            if isinstance(child, MessageNode):
                string.append(child.tostr(depth + 1))
            else:
                string.append(str(child))
                
        string = '\n'.join([('   '*depth +f) for f in string])
        return "message %s {\n%s\n%s}" % (self.name, string, '   '*(depth-1))
    def __str__(self):
        return self.tostr(1)
        
class FieldDescriptorNode(ParseNode):
    label = None
    number = None
    name = None
    type = None
    def __str__(self):
        t = self.type
        if isinstance(self.type, MessageNode):
            t = self.type.name
        return '{0} {1} {2} = {3};'.format(self.label, t, self.name,  self.number )
        
class EnumNode(ParseNode):
    def __str__(self):
        return 'enum %s { %s }' % (self.name, ' '.join(map(str, self.children)) )
        
class EnumAssignmentNode(ParseNode):
    def __str__(self):
        return '{0} = {1};'.format(self.name, self.value )
        
class OptionNode(ParseNode):
    def __str__(self):
        return 'option {0} = {1};'.format(self.name, self.value )
        
class ExtendNode(ParseNode):
    def __str__(self):
        return 'extend %s { %s }' % (self.name, ' '.join(map(str, self.children)) )
        
class OptionalNode(ParseNode):
    def __str__(self):
        return 'optional {0} {1} = {2};'.format(self.name, self.type, self.value )
        
class SyntaxNode(ParseNode):
    def __str__(self):
        return 'syntax = "{0}";'.format(self.value )
        
class ImportNode(ParseNode):
    def __str__(self):
        return 'import "{0}";'.format(self.value )
        
class ExtensionsNode(ParseNode):
    def __str__(self):
        return 'extension  {0} to {1};'.format(self.start, self.end )

