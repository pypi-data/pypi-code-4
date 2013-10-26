"""
Module containing GML constants and utility methods.
"""
from lxml import etree
import numpy

GML_NS = 'http://www.opengis.net/gml'
GML = '{%s}' % GML_NS
GML_ID = etree.QName(GML_NS, 'id')
GML_NAME = etree.QName(GML_NS, 'name')
GML_POLYGON = etree.QName(GML_NS, 'Polygon')
GML_POINT = etree.QName(GML_NS, 'Point')
GML_EXTERIOR = etree.QName(GML_NS, 'exterior')
GML_LINEAR_RING = etree.QName(GML_NS, 'LinearRing')
GML_POS_LIST = etree.QName(GML_NS, 'posList')
GML_POS = etree.QName(GML_NS, 'pos')
GML_LINE_STRING = etree.QName(GML_NS, 'LineString')

def _append_polygon(element, polygon_coords):
    """
    Append GML polygon to etree element.
    """
    polygon = etree.Element(GML_POLYGON)
    element.append(polygon)

    exterior = etree.Element(GML_EXTERIOR)
    polygon.append(exterior)

    linear_ring = etree.Element(GML_LINEAR_RING)
    exterior.append(linear_ring)
    coords= ' '.join([''.
        join(str(lon)+' '+str(lat)) for lon, lat in polygon_coords])
    pos_list = etree.Element(GML_POS_LIST)
    pos_list.text = coords
    linear_ring.append(pos_list)

def _get_polygon_from_2DLinestring(polygon):
    """
    Extract polygon coordinates from 2D line string.
    """
    poly_coords = polygon.split()
    poly_coords = numpy.array(poly_coords,dtype=float). \
        reshape(len(poly_coords)/2,2)

    return poly_coords

def _parse_3DLineString(line):
    """
    Parse and return 3d line string as numpy.array [[lon1, lat1, depth1], ...,
    [lon_N, lat_N, depth_N]]
    """
    line_coords = line.find('%s' % GML_POS_LIST).text.split()
    line_coords = numpy.array(line_coords,dtype=float). \
        reshape(len(line_coords)/3,3)

    return line_coords

def _append_3DLineString(element, line):
    """
    Append line string (3D)
    """
    line_string = etree.Element(GML_LINE_STRING)
    element.append(line_string)

    pos_list = etree.Element(GML_POS_LIST)
    coords= ' '.join([''.
        join(str(lon)+' '+str(lat)+' '+str(depth)) for lon, lat, depth in line])
    pos_list = etree.Element(GML_POS_LIST)
    pos_list.text = coords
    line_string.append(pos_list)

def _parse_2DPosList(pos_list):
    """
    Parse and return 2D pos list as numpy array
    [[lon1, lat1], ..., [lon_N, lat_N]]
    """
    line_coords = pos_list.text.split()
    line_coords = numpy.array(line_coords,dtype=float). \
        reshape(len(line_coords)/2,2)

    return line_coords

def _append_2DLineString(element, line):
    """
    Append line string (2D)
    """
    line_string = etree.Element(GML_LINE_STRING)
    element.append(line_string)

    pos_list = etree.Element(GML_POS_LIST)
    coords= ' '.join([''.
        join(str(lon)+' '+str(lat)) for lon, lat, _ in line])
    pos_list = etree.Element(GML_POS_LIST)
    pos_list.text = coords
    line_string.append(pos_list)