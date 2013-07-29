import itertools

from lxml import etree

from csat import graphml


class _AttributesProxyMixin(object):

    def __getitem__(self, key):
        return self._attributes[key]

    def __setitem__(self, key, value):
        self._attributes[key] = value

    def __delitem__(self, key):
        del self._attributes[key]

    def __iter__(self):
        return iter(self._attributes)

    def __contains__(self, item):
        return item in self._attributes


class Node(_AttributesProxyMixin, object):

    def __init__(self, graph, id, attributes=None):
        self._graph = graph
        self._id = int(id)
        self._attributes = attributes if attributes else {}
        self._subgraph = None
        self._edges = set()

    def __repr__(self):
        return 'Node({})'.format(self.id)

    @property
    def id(self):
        id = 'n' + str(self._id) if self._id is not None else None

        if self._graph._parent:
            id = '{}::{}'.format(self._graph._parent.id, id)

        return id

    @property
    def path(self):
        path = (self._id, )

        if self._graph._parent:
            path += self._graph._parent.path

        return path

    def subgraph(self, default_direction=None, attributes=None):
        if self._subgraph is not None:
            raise ValueError('This node already has a subgraph.')

        if default_direction is None:
            default_direction = self._graph.default_direction

        self._subgraph = Graph(None, default_direction, attributes,
                               _parent=self)
        return self._subgraph

    @classmethod
    def from_xml(cls, element, document, graph):
        id = int(element.get('id').rsplit('::')[-1][1:])
        self = cls(graph, id)
        ns = {'namespaces': graphml.xpath_nsmap}

        for data_el in element.xpath('./g:data', **ns):
            attr = BoundAttribute.from_xml(data_el, document)
            self._attributes[attr.name] = attr.value

        for graph_el in element.xpath('./g:graph', **ns):
            graph = Graph.from_xml(graph_el, document, self)
            self._subgraph = graph

        return self

    def to_xml(self, document, factory):
        node = factory('node')
        node.set('id', str(self.id))

        for k in self:
            try:
                attr = document.attrs[Attribute.NODE, k]
            except KeyError:
                continue
            else:
                node.append(attr.bind(self[k]).to_xml(document, factory))

        if self._subgraph is not None:
            node.append(self._subgraph.to_xml(document, factory))

        return node

    def merge(self, other):
        # Merge data
        self._attributes.update(other._attributes)

        # Merge subgraphs
        if other._subgraph is not None:
            if self._subgraph is None:
                self.subgraph(other._subgraph.default_direction)
            id_map = self._subgraph.merge(other._subgraph)
        else:
            id_map = None
        return id_map


class Edge(_AttributesProxyMixin, object):
    def __init__(self, graph, source_node, target_node, attributes=None,
                 id=None, directed=None):
        self._graph = graph
        self._source = source_node
        self._target = target_node
        self._attributes = attributes if attributes else {}
        self._id = int(id) if id is not None else None
        self._directed = directed
        self._source._edges.add(self)
        self._target._edges.add(self)

    @property
    def id(self):
        return 'e' + str(self._id) if self._id is not None else None

    def __repr__(self):
        symbol = '>' if self.directed else '-'
        return 'Edge({} {} {})'.format(self.source.id, symbol, self.target.id)

    @property
    def directed(self):
        if self._directed is None:
            return self._graph.directed
        else:
            return self._directed == Graph.DIRECTED

    @property
    def source(self):
        return self._source

    @property
    def target(self):
        return self._target

    @classmethod
    def from_xml(cls, element, document, graph):
        source = [int(t[1:]) for t in element.get('source').split('::')]
        target = [int(t[1:]) for t in element.get('target').split('::')]

        parent_graphs = graph.level()

        subgraph = graph
        for node_id in source[parent_graphs:-1]:
            subgraph = subgraph.nodes[node_id]._subgraph
        source_node = subgraph.nodes[source[-1]]

        subgraph = graph
        for node_id in target[parent_graphs:-1]:
            subgraph = subgraph.nodes[node_id]._subgraph
        target_node = subgraph.nodes[target[-1]]

        id = element.get('id', None)
        if id:
            id = int(id[1:])

        directed = element.get('directed', None)
        if directed:
            directed = directed == 'true'

        self = cls(graph, source_node, target_node, id=id, directed=directed)

        ns = {'namespaces': graphml.xpath_nsmap}

        for data_el in element.xpath('./g:data', **ns):
            attr = BoundAttribute.from_xml(data_el, document)
            self._attributes[attr.name] = attr.value

        return self

    def to_xml(self, document, factory):
        edge = factory('edge')
        edge.set('source', self._source.id)
        edge.set('target', self._target.id)

        if self.id is not None:
            edge.set('id', self.id)

        if self._directed is not None:
            edge.set('directed', 'true' if self._directed else 'false')

        for k in self:
            try:
                attr = document.attrs[Attribute.EDGE, k]
            except KeyError:
                continue
            else:
                edge.append(attr.bind(self[k]).to_xml(document, factory))

        return edge


def safe_unicode(obj, *args):
    if isinstance(obj, unicode):
        return obj

    try:
        if isinstance(obj, basestring):
            return unicode(obj, *args)
        else:
            return unicode(obj)
    except UnicodeDecodeError:
        ascii_text = str(obj).encode('string_escape')
        return unicode(ascii_text)


class Attribute(object):

    GRAPH, NODE, EDGE, ALL = 'graph', 'node', 'edge', 'all'

    CAST_FUNCTIONS = {
        'boolean': (lambda x: str(bool(x)), lambda x: bool(int(x.text))),
        'int': (lambda x: str(int(x)), lambda x: int(x.text)),
        'long': (lambda x: str(int(x)), lambda x: int(x.text)),
        'float': (lambda x: str(float(x)), lambda x: float(x.text)),
        'double': (lambda x: str(float(x)), lambda x: float(x.text)),
        'string': (lambda x: safe_unicode(x, 'utf8'), lambda x: safe_unicode(x.text)),
    }

    def __init__(self, graph, id, domain, name, type, default=None,
                 cast_func=None):
        assert type in self.CAST_FUNCTIONS
        self._graph = graph
        self._id = id
        self._domain = domain
        self._name = name
        self._type = type
        self._cast_func = cast_func if cast_func else self.CAST_FUNCTIONS[type]
        self._default = default

    @property
    def id(self):
        return 'd' + str(self._id)

    @property
    def name(self):
        return self._name

    @property
    def domain(self):
        return self._domain

    @classmethod
    def from_xml(cls, element, document):
        ns = {'namespaces': graphml.xpath_nsmap}
        id = int(element.get('id')[1:])
        domain = element.get('for')
        name = element.get('attr.name')
        type = element.get('attr.type', 'string')
        default = element.xpath('g:default/text()', **ns)
        default = default[0] if default else None

        self = cls(document, id, domain, name, type, default)

        return self

    def to_xml(self, document, factory):
        key = factory('key', {
            'id': self.id,
            'for': self._domain,
            'attr.name': self._name,
            'attr.type': self._type,
        })

        if self._default is not None:
            default = factory('default')
            default.text = self._cast_func[0](self._default)
            key.append(default)

        return key

    def bind(self, value):
        return BoundAttribute(self, value)

    def cast(self, value):
        return self._cast_func[0](value)

    def to_python(self, element):
        return self._cast_func[1](element)


class BoundAttribute(object):
    def __init__(self, attr, value):
        self._attribute = attr
        self._value = value

    @property
    def key(self):
        return self._attribute.id

    @property
    def name(self):
        return self._attribute.name

    @property
    def value(self):
        return self._value

    def to_xml(self, document, factory):
        attr = factory('data')
        attr.set('key', self.key)
        attr.text = self._attribute.cast(self._value)
        return attr

    @classmethod
    def from_xml(cls, element, document):
        id = int(element.get('key')[1:])
        attr = document.attrs[id]
        value = attr.to_python(element)
        return cls(attr, value)


class GraphMLFactory(object):

    nsmap = {
        None: graphml.namespace,
        'xsi': 'http://www.w3.org/2001/XMLSchema-instance',
    }

    def qname(self, name_or_namespaced, isattr=False):
        if isinstance(name_or_namespaced, basestring):
            namespace, name = None, name_or_namespaced
        else:
            namespace, name = name_or_namespaced

        if isattr and not namespace:
            return name
        return '{{{}}}{}'.format(self.nsmap[namespace], name)

    def element(self, name, attributes={}):
        element = etree.Element(self.qname(name), nsmap=self.nsmap)

        for name, value in attributes.iteritems():
            element.set(self.qname(name, isattr=True), str(value))

        return element

    __call__ = element


class Graph(_AttributesProxyMixin, object):
    """
    Generic class to build graph-like data structures with extended support for
    reading and writing files in the GraphML format. The class itself does not
    offer any graph-related algorithms.
    """

    # Not implemented:
    # - Ports
    # - Hyperedges
    # - Multiple, non-nested graphs

    UNDIRECTED, DIRECTED = range(2)

    def __init__(self, id=None, default_direction=UNDIRECTED, attributes=None,
                 _parent=None):
        self._id = int(id) if id is not None else None
        self._default_direction = default_direction
        self._attributes = attributes if attributes else {}
        self._nodes = {}
        self._edges = {}
        self._parent = _parent
        self._attribute_definitions = {}

    @classmethod
    def from_xml(cls, element, document, parent=None):
        ns = {'namespaces': graphml.xpath_nsmap}

        direction = element.get('edgedefault')
        direction = (Graph.UNDIRECTED if direction == 'undirected'
                     else Graph.DIRECTED)
        id = element.get('id', None)
        if not parent:
            id = int(id[1:]) if id else get_unique_id(document._graphs)
        else:
            id = None
        self = Graph(id, direction, _parent=parent)

        # Data
        for data_el in element.xpath('./g:data', **ns):
            attr = BoundAttribute.from_xml(data_el, document)
            self._attributes[attr.name] = attr.value

        # Nodes
        for node_el in element.xpath('./g:node', **ns):
            node = Node.from_xml(node_el, document, self)
            self._nodes[node._id] = node

        # Edges
        for edge_el in element.xpath('./g:edge', **ns):
            edge = Edge.from_xml(edge_el, document, self)
            key = (edge.source, edge.target)
            if key not in self._edges:
                self._edges[key] = set()
            self._edges[key].add(edge)

        return self

    @property
    def default_direction(self):
        return self._default_direction

    @property
    def id(self):
        if self._parent:
            return '{}:'.format(self._parent.id)
        else:
            return 'g' + str(self._id) if self._id is not None else None

    @property
    def nodes(self):
        return self._nodes

    @property
    def edges(self):
        return self._edges

    @property
    def directed(self):
        return self.default_direction == Graph.DIRECTED

    def iterparents(self, include_self=True):
        parent = self

        if include_self:
            yield self

        while parent._parent:
            parent = parent._parent._graph
            yield parent

    def level(self):
        level = 0

        while self._parent:
            self = self._parent._graph
            level += 1

        return level

    def node(self, id=None, attributes=None):
        """
        Adds a new node to the graph with ID C{id}.

        @type  id: C{int}
        @param id: The ID to assign to this node.

        @rtype: L{Node}
        @return: An instance of L{Node}.

        @raise: L{KeyError} if the node already exists.
        """
        if id is not None:
            id = int(id)
            if id in self._nodes:
                raise KeyError('Node with ID {:d} already exists.'.format(id))
        else:
            id = get_unique_id(self._nodes)

        node = Node(self, id, attributes)
        self._nodes[id] = node
        return node

    def remove_node(self, node):
        for edge in node._edges:
            edge._graph.remove_edge(edge)
        try:
            del self._nodes[node._id]
        except KeyError:
            pass

    def edge(self, source_node, target_node, attributes=None, id=None,
             directed=None):
        """
        Adds a new edge between the C{source_node} and C{target_node}. As this
        class implements multigraph support, a new edge is added even if one
        already exists between the two specified nodes.
        """
        if not isinstance(source_node, Node):
            source_node = self._nodes[int(source_node)]

        if not isinstance(target_node, Node):
            target_node = self._nodes[int(target_node)]

        edge = Edge(self, source_node, target_node, attributes, id, directed)
        key = (source_node, target_node)

        try:
            edges = self._edges[key]
        except KeyError:
            edges = self._edges[key] = set()
        edges.add(edge)
        return edge

    def remove_edge(self, edge):
        key = (edge.source, edge.target)
        try:
            edges = self._edges[key]
        except KeyError:
            pass
        else:
            edges.discard(edge)

    def to_xml(self, document, factory):
        graph = factory('graph', {
            'id': self.id,
            'edgedefault': 'directed' if self.directed else 'undirected',
        })

        nodes, edges = 0, 0

        for k in self:
            try:
                attr = document.attrs[Attribute.GRAPH, k]
            except KeyError:
                continue
            else:
                graph.append(attr.bind(self[k]).to_xml(document, factory))

        for node in self._nodes.itervalues():
            graph.append(node.to_xml(document, factory))
            nodes += 1

        for edge in itertools.chain.from_iterable(self._edges.itervalues()):
            graph.append(edge.to_xml(document, factory))
            edges += 1

        graph.set('parse.nodes', str(nodes))
        graph.set('parse.edges', str(edges))
        graph.set('parse.nodeids', 'canonical')
        graph.set('parse.order', 'nodesfirst')
        graph.set('parse.edgeids', 'canonical')

        return graph

    def merge(self, other):
        id_map = {}

        try:
            key = self['merge_key']
            key = key if key == other['merge_key'] else None
        except KeyError:
            key = None

        # Copy attributes
        self._attributes.update(other._attributes)

        # Merge or copy nodes
        for othernode in other.nodes.itervalues():
            copy = False
            if key:
                try:
                    otherkey = othernode[key]
                except KeyError:
                    copy = True
                else:
                    for thisnode in self.nodes.itervalues():
                        thiskey = thisnode[key]
                        if thiskey == otherkey:
                            submap = thisnode.merge(othernode)
                            id_map[othernode._id] = thisnode._id, submap
                            break
                    else:
                        copy = True
            else:
                copy = True

            if copy:
                # Copy node over
                id = get_unique_id(self._nodes)
                thisnode = self.node(id)
                submap = thisnode.merge(othernode)
                id_map[othernode._id] = thisnode._id, submap

        return self._copy_edges(other, id_map)

    def _copy_edges(self, other, id_map):
        depth = len(self._parent.path) if self._parent else 0

        def node_from_path(parent_graph, id_map, path):
            path = list(path)
            parent_graph = self

            while len(path) > 1:
                old_parent_id = path.pop()
                new_parent_id, id_map = id_map[old_parent_id]
                parent_graph = parent_graph._nodes[new_parent_id]._subgraph

            old_node_id = path.pop()
            assert len(path) == 0
            new_node_id, _ = id_map[old_node_id]
            new_node = parent_graph._nodes[new_node_id]
            return new_node

        for edge in itertools.chain.from_iterable(other._edges.itervalues()):
            try:
                srcpath = edge.source.path
                if depth:
                    srcpath = srcpath[:-depth]
                srcnode = node_from_path(self, id_map, srcpath)
                dstpath = edge.target.path
                if depth:
                    dstpath = dstpath[:-depth]
                dstnode = node_from_path(self, id_map, dstpath)
                self.edge(srcnode, dstnode, edge._attributes, None,
                          edge._directed)
            except KeyError:
                raise

        return id_map


def get_unique_id(collection, id=None):
    if id is None:
        id = len(collection)
        while id in collection:
            id += 1
    else:
        id = int(id)
        if id in collection:
            raise KeyError('ID {} is already known.'.format(id))

    return id


class AttributeDeclarationGetter(object):
    def __init__(self, by_domain, by_id):
        self._by_domain = by_domain
        self._by_id = by_id

    def __getitem__(self, key):
        try:
            domain, name = key
        except TypeError:
            return self._by_id[key]
        else:
            try:
                return self._by_domain[domain, name]
            except KeyError as e:
                if domain != Attribute.ALL:
                    try:
                        return self._by_domain[Attribute.ALL, name]
                    except KeyError:
                        pass
                raise e


class GraphMLDocument(object):

    def __init__(self):
        self._attributes_by_domain = {}
        self._attributes_by_id = {}
        self.attrs = AttributeDeclarationGetter(self._attributes_by_domain,
                                                self._attributes_by_id)
        self._graphs = {}

    @property
    def graphs(self):
        return self._graphs

    def attr(self, domain, name, type='string', default=None, cast_func=None,
             id=None):
        id = get_unique_id(self._attributes_by_id, id)
        attr = Attribute(self, id, domain, name, type, default, cast_func)
        self._attributes_by_domain[domain, name] = attr
        self._attributes_by_id[id] = attr
        return attr

    def _add_graph(self, id, default_direction, attributes):
        self._graphs[id] = Graph(id, default_direction, attributes)
        return self._graphs[id]

    def graph(self, id=None, attributes=None):
        id = get_unique_id(self._graphs, id)
        return self._add_graph(id, Graph.UNDIRECTED, attributes)

    def digraph(self, id=None, attributes=None):
        id = get_unique_id(self._graphs, id)
        return self._add_graph(id, Graph.DIRECTED, attributes)

    def to_xml(self, factory=None):
        if factory is None:
            factory = GraphMLFactory()

        root = factory.element('graphml', {
            ('xsi', 'schemaLocation'): (
                'http://graphml.graphdrawing.org/xmlns '
                'http://graphml.graphdrawing.org/xmlns/1.0/graphml.xsd'
            ),
        })

        for attr in self._attributes_by_id.itervalues():
            root.append(attr.to_xml(self, factory))

        for graph in self._graphs.itervalues():
            root.append(graph.to_xml(self, factory))

        return root

    @classmethod
    def from_xml(cls, element):
        self = cls()

        ns = {'namespaces': graphml.xpath_nsmap}

        # Data attribute definition
        for attr_el in element.xpath('/g:graphml/g:key', **ns):
            attr = Attribute.from_xml(attr_el, self)
            self._attributes_by_domain[attr.domain, attr.name] = attr
            self._attributes_by_id[attr._id] = attr

        # Graphs
        for graph_el in element.xpath('/g:graphml/g:graph', **ns):
            graph = Graph.from_xml(graph_el, self)
            self._graphs[graph._id] = graph

        return self

    def to_file(self, stream):
        doc = self.to_xml()
        docstr = etree.tostring(
            doc, xml_declaration=True, encoding='utf-8', pretty_print=True
        ).strip()
        stream.write(docstr)
        return stream

    @classmethod
    def from_file(cls, stream):
        doc = etree.parse(stream)
        return cls.from_xml(doc)

    def merge(self, other):
        for attr in other._attributes_by_id.values():
            try:
                self._attributes_by_domain[attr._domain, attr._name]
            except KeyError:
                self.attr(attr._domain, attr._name, attr._type, attr._default,
                          attr._cast_func)

        try:
            [g1] = self.graphs.values()
        except ValueError:
            g1 = self.graph()

        if other.graphs:
            [g2] = other.graphs.values()
        g1.merge(g2)

    def normalized(self):
        doc = GraphMLDocument()
        doc.merge(self)
        return doc


class GraphMLWriter(object):
    def __init__(self, doc):
        self.doc = doc

    def write_graphml(self, stream):
        return self.doc.normalized().to_file(stream)


def merge_graphs(documents, into=None):
    if into is None:
        into = GraphMLDocument()
    for d in documents:
        into.merge(d)
    return into


def merge_files(files, into=None):
    def graph_gen(files):
        for file in files:
            if isinstance(file, basestring):
                with open(file) as fh:
                    yield GraphMLDocument.from_file(fh)
            else:
                yield GraphMLDocument.from_file(file)

    if into:
        with open(into) as fh:
            into = GraphMLDocument.from_file(fh)
    return merge_graphs(graph_gen(files), into)


if __name__ == '__main__':

    d = GraphMLDocument()
    d.attr(Attribute.GRAPH, 'domain', 'string')
    d.attr(Attribute.NODE, 'weight', 'float', default=2)

    g = d.graph('1', Graph.DIRECTED, {'domain': 'testing'})
    n1 = g.node(1, {
        'weight': 1.0,
    })
    n2 = g.node(2)
    n3 = g.node(3)
    n4 = g.node(4)
    n5 = g.node(5)

    g2 = n2.subgraph()
    n21 = g2.node(1)
    n22 = g2.node(2)
    e21 = g2.edge(n21, n22)

    g3 = n21.subgraph()
    g3.node(2)

    e1 = g.edge(n1, n2, id=2)
    e2 = g.edge(n1, n2, directed=True)
    e3 = g.edge(n2, n1, directed=False)

    docu = d.to_xml()

    print etree.tostring(
        docu, xml_declaration=True, encoding='utf-8', pretty_print=True
    ).strip()

    #graphml.get_schema().assertValid(doc)
    #graphml.get_dtd().assertValid(doc)

    gb = GraphMLDocument.from_xml(docu)
    print etree.tostring(
        gb.to_xml(), xml_declaration=True, encoding='utf-8', pretty_print=True
    ).strip()
