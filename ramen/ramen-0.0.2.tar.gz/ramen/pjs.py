__all__ = [
    'PJS'
]


def escape_value(value):
    if type(value) in [str, unicode]:
        value = '"{0}"'.format(value)
    return value


class Attr(dict):
    
    def __str__(self):
        if self['namespace']:
            return u'{namespace}.{attr_name}'.format(**self)
        else:
            return self['attr_name']


class AttrAccessor(object):

    def __init__(self, attr_name):
        self.attr_name = attr_name

    def __get__(self, obj, owner):
        attr = Attr()
        attr['namespace'] = obj.namespace
        attr['attr_name'] = self.attr_name
        return attr

    def __set__(self, obj, value):
        obj.root.context.nodes.append(u'{0}.{1} = {2}'.format(obj.namespace, self.attr_name, escape_value(value)))

    def __del__(self, obj):
        pass


class Node(object):
    
    html = AttrAccessor('innerHTML')
    text = AttrAccessor('innerText')

    def __init__(self, selector=None, parent=None, level=0, multi=False, var=None, namespace=''):

        self.selector = selector
        self.parent = parent
        self.level = level+1
        self.multi = multi
        self.nodes = []
        self.var = var
        self.namespace = namespace and namespace+namespace[-1] or var[0]

        self.delim = u'\n' + '\t'*self.level

        if not parent:
            self.root = self
            self.context = self
        else:
            self.root = parent.root

    def __enter__(self):
        self.root.context = self

        return self

    def __exit__(self, e,v,t):
        self.root.context = self.parent
        if self.parent:
            self.parent.add_node(self)

    def add_node(self, node):
        self.nodes.append(node.render())

    def get_selector(self):
        if self.selector:
            return u'{0}.querySelector{1}("{2}")'.format(self.parent.namespace, self.multi and 'All' or '', self.selector)

        if self.parent:
            return u'{0}.{1}'.format(self.parent.namespace, self.var)
        else:
            return self.var

    def e(self, selector):
        return Node(selector=selector, parent=self, level=self.level, multi=False, namespace=self.namespace)

    def el(self, selector):
        return Node(selector=selector, parent=self, level=self.level, multi=True, namespace=self.namespace)

    def render(self):
        return u'(function({0}){{{3}{2};{4}}})({1})'.format(
                self.namespace, 
                self.get_selector(),                 
                ';{0}'.format(self.delim).join(self.nodes),
                self.delim,
                self.delim[:-1]
            )


class Window(Node):

    @property
    def document(self):
        return Node(var='document', parent=self, level=1)


class PJSDescriptor(object):

    def __init__(self, klass, kwargs):
        self.klass = klass
        self.kwargs = kwargs

    def __get__(self, obj, owner):
        node = self.klass(**self.kwargs)
        obj._node = node
        return node

    def __set__(self, obj, value):
        pass

class PJS(object):
        
    window = PJSDescriptor(Window, {'var':'window'})
    document = PJSDescriptor(Node, {'var':'document'})
    _node = None

    def __init__(self):
        self._node = None
        
    def __enter__(self):
        return self

    def __exit__(self, e, v, t):
        pass

    def __getattr__(self, attr):
        if vars(self).has_key(attr):
            return vars(self)[attr]
        else: 
            return Attr(attr_name=attr, namespace=None)

    def __setattr__(self, attr, value):        
        if attr in ['_node', 'window', 'document']:
            vars(self)[attr] = value
        else:
            self._node.context.nodes.append(u'{0} = {1}'.format(attr, escape_value(value)))

    def var(self, var):
        defines = []
        if type(var) == list:          
            defines.extend(var)  
        elif type(var) == dict:
            defines.extend(['{0} = {1}'.format(name, escape_value(value)) for name, value in var.items()])
        else:
            defines.append(var)

        self._node.context.nodes.append(u'var {0}'.format(', '.join(defines)))

    def render(self):
        return self._node.render()
