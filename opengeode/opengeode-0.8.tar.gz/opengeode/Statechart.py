#!/usr/bin/env python

"""
    OpenGEODE - A tiny, free SDL Editor for TASTE

    SDL is the Specification and Description Language (Z100 standard from ITU)

    Copyright (c) 2012 European Space Agency

    Designed and implemented by Maxime Perrotin

    This module is responsible for the rendering of statecharts using
    the graphviz library.

    Credits:
    Rendering algorithm to transform graphviz b-splines to to Qt bezier curves
    was developed by Steve Dodier-Lazaro (www.mupuf.org)

    Contact: maxime.perrotin@esa.int
"""

import math
import PySide
import genericSymbols
import logging
try:
    import pygraphviz as dotgraph
except ImportError:
    print('pygraphviz not found. Statechart modulew will not work\n'
            'If you are using Debian (or Ubuntu) you can install it from\n'
            'the official depots: sudo apt-get install python-pygraphviz')

RENDER_DPI = {'X': 93.0, 'Y': 95.0}
G_SYMBOLS = set()
EDGES = []

LOG = logging.getLogger(__name__)

# pylint: disable=R0904
class Record(genericSymbols.HorizontalSymbol, object):
    ''' Graphviz node - it is floating and has no parent'''
    allowed_followers = ['Record', 'Diamond']
    textbox_alignment = (PySide.QtCore.Qt.AlignTop
                         | PySide.QtCore.Qt.AlignHCenter)

    def __init__(self, node, graph):
        ''' Initialization: compute the polygon shape '''
        self.name = node['name']
        super(Record, self).__init__(x=node['pos'][0],
                y=node['pos'][1], text=self.name)
        self.set_shape(node['width'], node['height'])
        self.setBrush(PySide.QtGui.QBrush(PySide.QtGui.QColor(255, 255, 202)))
        self.graph = graph
        if 'properties' in node:
            property_box = PySide.QtGui.QGraphicsTextItem(self)
            property_box.setPos(5, 30)
            property_box.setPlainText(node['properties'])

    def set_shape(self, width, height):
        ''' Define the polygon shape from width and height '''
        path = PySide.QtGui.QPainterPath()
        path.moveTo(0, 25)
        path.lineTo(width, 25)
        # check if adding mode = Qt.RelativeSize would not be better
        path.addRoundedRect(0, 0, width, height, 15, 15)
        self.setPath(path)
        super(Record, self).set_shape(width, height)

    def resize_item(self, _):
        ''' Redefine the resizing function - forbid resizing '''
        pass

    def __str__(self):
        ''' User-friendly information about the node '''
        return('Node ' + self.name + ' at pos ' + str(self.pos()) +
                ' bounding rect = ' + str(self.boundingRect()))

    def mouse_move(self, event):
        ''' Handle mouse move: update the edge on the fly '''
        super(Record, self).mouse_move(event)
        delta_pos = event.pos() - event.lastPos()
        delta = [delta_pos.x(), delta_pos.y()]
        for edge in edges(self.scene(), self):
            if edge.edge['source'] == self:
                edge.edge['start'] = [
                        sum(u) for u in zip(edge.edge['spline'][0], delta)]
                edge.edge['spline'][0] = edge.edge['start']
            if edge.edge['target'] == self:
                edge.edge['end'] = [
                        sum(u) for u in zip(edge.edge['end'], delta)]
                edge.edge['spline'][-1] = edge.edge['end']
                #[edge.edge['end'][d] + delta[d]
                #                    for d in range(2)]
            edge.reshape()

    def mouse_release(self, _):
        ''' After moving item, ask dot to recompute the edges '''
        #update(self.scene())
        # Discard mouse release default action
        pass


# pylint: disable=R0904
class Point(genericSymbols.HorizontalSymbol, object):
    ''' Graphviz point node - used for START transition'''
    allowed_followers = ['Record', 'Diamond']
    textbox_alignment = (PySide.QtCore.Qt.AlignTop
                         | PySide.QtCore.Qt.AlignHCenter)

    def __init__(self, node, graph):
        ''' Initialization: compute the polygon shape '''
        self.name = node['name']
        super(Point, self).__init__(x=node['pos'][0],
                y=node['pos'][1], text='')
        self.set_shape(node['width'], node['height'])
        self.setBrush(PySide.QtGui.QBrush(PySide.QtCore.Qt.black))
        self.graph = graph

    def set_shape(self, width, height):
        ''' Define the polygon shape from width and height '''
        path = PySide.QtGui.QPainterPath()
        path.addEllipse(0, 0, width, height)
        self.setPath(path)
        super(Point, self).set_shape(width, height)
    
    def resize_item(self, _):
        ''' Redefine the resizing function - forbid resizing '''
        pass

    def __str__(self):
        ''' User-friendly information about the node '''
        return('Point ' + self.name + ' at pos ' + str(self.pos()) +
                ' bounding rect = ' + str(self.boundingRect()))

    def mouse_release(self, _):
        ''' After moving item, ask dot to recompute the edges '''
        #self.scene().refresh()        
        update(self.scene())


# pylint: disable=R0904
class Diamond(genericSymbols.HorizontalSymbol, object):
    ''' Graphviz node - it is floating and has no parent'''
    allowed_followers = ['Record']
    textbox_alignment = (PySide.QtCore.Qt.AlignTop
                         | PySide.QtCore.Qt.AlignHCenter)

    def __init__(self, node, graph):
        ''' Initialization: compute the polygon shape '''
        self.name = node['name']
        super(Diamond, self).__init__(x=node['pos'][0],
                y=node['pos'][1], text='')
        self.set_shape(node['width'], node['height'])
        #self.setBrush(PySide.QtGui.QBrush(PySide.QtCore.Qt.black))
        self.graph = graph

    def set_shape(self, width, height):
        ''' Define the polygon shape from width and height '''
        path = PySide.QtGui.QPainterPath()
        path.moveTo(width / 2, 0)
        path.lineTo(width, height / 2)
        path.lineTo(width / 2, height)
        path.lineTo(0, height / 2)
        path.lineTo(width / 2, 0)
        self.setPath(path)
        super(Diamond, self).set_shape(width, height)
    
    def resize_item(self, _):
        ''' Redefine the resizing function - forbid resizing '''
        pass

    def __str__(self):
        ''' User-friendly information about the node '''
        return('Node ' + self.name + ' at pos ' + str(self.pos()) +
                ' bounding rect = ' + str(self.boundingRect()))

    def mouse_release(self, _):
        ''' After moving item, ask dot to recompute the edges '''
        #self.scene().refresh()        
        update(self.scene())


class Edge(genericSymbols.Connection, object):
    ''' B-spline/Bezier connection shape '''
    def __init__(self, edge, graph):
        ''' Set generic parameters from Connection class '''
        super(Edge, self).__init__(edge['source'], edge['target'])
        self.edge = edge
        self.graph = graph
        #self.setBrush(PySide.QtGui.QBrush(PySide.QtGui.QColor(0, 0, 255)))
        self.reshape()

    # pylint: disable=R0914
    def reshape(self):
        ''' Update the shape of the edge (redefined function) '''
        path = PySide.QtGui.QPainterPath()
        assert(len(self.edge['spline']) % 3 == 1)
        # If there is a starting point, draw
        # a line from it to the first curve point
        if self.edge.get('start'):
            path.moveTo(self.mapFromScene(*self.edge['start']))
            path.lineTo(self.mapFromScene(*self.edge['spline'][0]))
        else:
            path.moveTo(self.mapFromScene(*self.edge['spline'][0]))
        # Loop over the curve points:
        for i in xrange(1, len(self.edge['spline']), 3):
            c_1 = self.mapFromScene(
                    PySide.QtCore.QPointF(*self.edge['spline'][i]))
            c_2 = self.mapFromScene(
                    PySide.QtCore.QPointF(*self.edge['spline'][i + 1]))
            end_point = self.mapFromScene(
                    PySide.QtCore.QPointF(*self.edge['spline'][i + 2]))
            path.cubicTo(c_1, c_2, end_point)
        # If there is an ending point, draw a line to it
        if self.edge.get('end'):
            path.lineTo(self.mapFromScene(*self.edge['end']))

        # Draw the arrow head
        length = path.length()
        percent = path.percentAtLength(length - 10.0)
        src = path.pointAtPercent(percent)
        #angle = path.angleAtPercent(percent)
        #print angle
        end_point = path.currentPosition()
        line = PySide.QtCore.QLineF(src, end_point)
        angle = math.acos(line.dx() / line.length())
        if line.dy() >= 0:
            angle = math.pi * 2 - angle
        arrow_size = 10.0 
        arrow_p1 = end_point + PySide.QtCore.QPointF(
                math.sin(angle - math.pi/3) * arrow_size,
                math.cos(angle - math.pi/3) * arrow_size)
        arrow_p2 = end_point + PySide.QtCore.QPointF(
                math.sin(angle - math.pi + math.pi/3) * arrow_size,
                math.cos(angle - math.pi + math.pi/3) * arrow_size)
        path.lineTo(arrow_p1)
        path.lineTo(end_point)
        path.lineTo(arrow_p2)
        path.moveTo(end_point)
        try:
            font = PySide.QtGui.QFont('arial', pointSize = 8)
            width = PySide.QtGui.QFontMetrics(font).width(self.edge['label'])
            pos = self.mapFromScene(*self.edge['lp'])
            path.addText(pos.x() - width/2, pos.y(),
                    font, self.edge['label'])
        except KeyError:
            # no label
            pass
        self.setPath(path)

    def __str__(self):
        ''' user-friendly information about the edge coordinates '''
        return('Edge between ' + self.edge['source'].name + ' and ' +
                self.edge['target'].name + str(self.edge['spline'][0]))

    def paint(self, painter, _, ___):
        ''' Apply anti-aliasing to Edge Connections '''
        painter.setRenderHint(PySide.QtGui.QPainter.Antialiasing, True)
        super(Edge, self).paint(painter, _, ___)


def edges(scene, node):
    ''' Return all edges of a given node '''
    for item in scene.items():
        if isinstance(item, Edge) and node in (
                item.edge['source'], item.edge['target']):
            yield item


# Front end part - use Graphviz to parse the input file and transform it
# pylint: disable=R0914
def preprocess_edges(my_graph, nodes, bounding_rect, dpi):
    ''' Parse edges and put them in a clean datastructure '''
    edges = []
    bb_height = bounding_rect[3]
    for edge in my_graph.edges_iter():
        new_edge = {}
        source, target = edge
        for node in nodes:
            if node.name == source:
                new_edge['source'] = node
            if node.name == target:
                new_edge['target'] = node
        new_edge['label'] = edge.attr.get('label')
        try:
            new_edge['lp'] = [float(val) for val in edge.attr['lp'].split(',')]
        except (ValueError, AttributeError):
            pass
        else:
            # translate the label position from dot-coordinates to Qt
            new_edge['lp'][0] *= RENDER_DPI['X'] / dpi
            new_edge['lp'][1] = (
                    bb_height - new_edge['lp'][1]) * (RENDER_DPI['Y'] / dpi)

        pos = edge.attr['pos'].split()

        if pos[0].startswith('e'):
            new_edge['end'] = [float(val)
                    for val in pos.pop(0).split(',')[1:]]
            # And translate position
            new_edge['end'][0] *= (RENDER_DPI['X'] / dpi)
            new_edge['end'][1] = (
                    bb_height - new_edge['end'][1]) * (RENDER_DPI['Y'] / dpi)

        elif pos[0].startswith('s'):
            new_edge['start'] = [float(val)
                    for val in pos.pop(0).split(',')[1:]]
            # And translate position
            new_edge['start'][0] *= (RENDER_DPI['X'] / dpi)
            new_edge['start'][1] = (
                    bb_height - new_edge['start'][1]) * (RENDER_DPI['Y'] / dpi)

        spline = []
        for entry in pos:
            point = [float(val) for val in entry.split(',')]
            point[0] *= (RENDER_DPI['X'] / dpi)
            point[1] = (bb_height - point[1]) * (RENDER_DPI['Y'] / dpi)

            spline.append(point)
        new_edge['spline'] = spline
        edges.append(new_edge)
    return edges


def preprocess_nodes(my_graph, bounding_rect, dpi):
    ''' Parse the nodes from the graph and create a clean datastructure '''
    # Graphviz calculates coordinates starting on the bottom-left corner,
    # while Qt uses the top-left corner, so we must translate all y-coord.
    bb_height = bounding_rect[3]
    nodes = []
    for node in my_graph.nodes_iter():
        new_node = {}
        # Get the node shape attribute - default is record
        new_node['shape'] = node.attr.get('shape') or 'record'
        # node main name
        new_node['name'] = str(node)
        try:
            # node complete label (can contain several compartments)
            properties = (
                    node.attr['label'][1:-2].split('|')[1].replace('\\', '\n'))
            new_node['properties'] = properties  # node.attr.get('label')
        except IndexError:
            pass
        # transform width and height from inches to pixels
        new_node['width'] = float(node.attr.get('width')) * RENDER_DPI['X']
        new_node['height'] = float(node.attr.get('height')) * RENDER_DPI['Y']
        # get the position of the CENTER of the node
        center_pos = [float(val)
                for val in node.attr.get('pos').split(',')]
        # apply dpi-conversion from 72 to 96
        center_pos[0] *= (RENDER_DPI['X'] / dpi)

        # translate y-coord from bottom-left to top-left corner
        center_pos[1] = (
                bb_height - center_pos[1]) * (RENDER_DPI['Y'] / dpi)
        new_node['pos'] = [center_pos[0] - (new_node['width'] / 2.0),
                           center_pos[1] - (new_node['height'] / 2.0)]
        nodes.append(new_node)
    return nodes


def update(scene):
    '''
        Parse the graph symbols and create a graphviz graph
        Used to update the edges in case user moves nodes.
    '''
    nodes = [{'name':node.name, 'pos':
        node.mapToScene(node.boundingRect().center()),
        'shape': type(node), 'width': node.boundingRect().width(),
        'height': node.boundingRect().height()}
        for node in scene.items() if isinstance(node,
                                               (Point, Diamond, Record))]
    graph = dotgraph.AGraph(
            strict=False, directed=True, splines='spline', start='rand')

    lookup = {Point: 'point', Record: 'record', Diamond: 'diamond'}
    for node in nodes:
        center_pos = node['pos']
        bb_height = scene.itemsBoundingRect().height()

        dpi = 72.0

        # Convert to graphviz coordinates / adapt DPI
        center_x = center_pos.x() * (dpi / RENDER_DPI['X'])
        center_y = (bb_height - center_pos.y()) * (dpi / RENDER_DPI['Y'])

        pos = unicode('{x},{y}'.format(x=int(center_x), y=int(center_y)))

        #print node['name'], node['height'], node['height'] / RENDER_DPI['Y']

        if node['shape'] in (Point, Diamond):
            graph.add_node(node['name'], pos=pos, shape=lookup[node['shape']],
                fixedsize='true', width=node['width'] / RENDER_DPI['X'],
                height=node['height'] / RENDER_DPI['Y'])
        else:
            graph.add_node(node['name'], pos=pos, shape=lookup[node['shape']])

    # Keep edges from the previous graph
    for edge in EDGES:
        graph.add_edge(edge, label=edge.attr.get('label') or '')

    #print graph.to_string()
    if nodes:
        #before = scene.itemsBoundingRect().center()
        render_statechart(scene, graph, keep_pos=True)
        #delta = scene.itemsBoundingRect().center() - before
        # graphviz translates the graph to pos (0, 0) -> move it back
        # to the exact graphical position where the user clicked
        #for item in scene.items():
        #    if isinstance(item, genericSymbols.Symbol):
        #        item.setPos(item.pos() - delta)


def render_statechart(scene, graph=None, keep_pos=False):
    ''' Render a graphviz/dot statechart on the QGraphicsScene '''
    # Statechart symbols lookup table
    lookup = {'point': Point, 'record': Record, 'diamond': Diamond}
    try:
        # Bonus: the tool can render any dot graph...
        graph = graph or dotgraph.AGraph('taste.dot')
    except IOError:
        LOG.info('No statechart to display....')
        raise
    graph.graph_attr.update(dpi='72.0')
    EDGES[:] = graph.edges()

    scene.clear()
    G_SYMBOLS.clear()

    # Compute all the coordinates (self-modifying function)
    # Force the fontsize of the nodes to be 12, as in OpenGEODE
    # use -n2 below to keep user-specified node coordinates 
    graph.layout(prog='neato', args=
            '-Nfontsize=12, -Gsplines=true -Gsep=1 -Gstart=random10 '
            '-Nstyle=rounded -Nshape=record -Elen=1.5 {kp}'
            .format(kp='-n1' if keep_pos else ''))
    # bb is not visible directly - extract it from the low level api:
    bounding_rect = [float(val) for val in
            dotgraph.graphviz.agget(graph.handle, 'bb').split(',')]
    dot_dpi = float(dotgraph.graphviz.agget(graph.handle, 'dpi'))
    # dot uses a 72 dpi value for converting its position coordinates
    # Get actual rendering DPI from Qt view
    for view in scene.views():
        RENDER_DPI['X'] = view.physicalDpiX()
        RENDER_DPI['Y'] = view.physicalDpiY()

    #fontname = graph.graph_attr.get('fontname')
    #fontsize = graph.graph_attr.get('fontsize')
    #print 'AFTER PROCESSING: ', graph.to_string()

    nodes = preprocess_nodes(graph, bounding_rect, dot_dpi)
    node_symbols = []
    for node in nodes:
        shape = node.get('shape')
        try:
            node_symbol = lookup[shape](node, graph)
        except KeyError:
            raise TypeError('Statechart - unsupported shape: ' + shape)
        G_SYMBOLS.add(node_symbol)
        node_symbols.append(node_symbol)
        scene.addItem(node_symbol)
    edges = preprocess_edges(graph, node_symbols, bounding_rect, dot_dpi)

    for edge in edges:
        Edge(edge, graph)


if __name__ == '__main__':
    render_statechart(None)
