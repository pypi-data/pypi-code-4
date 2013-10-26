"""
Module containing NRML 0.3 constants and utility methods.
"""
from lxml import etree
import gml
import numpy
from openquake.hazardlib.geo import Point

NRML03_NS = 'http://openquake.org/xmlns/nrml/0.3'
NRML03 = '{%s}' % NRML03_NS
NRML03_AREA_SOURCE = etree.QName(NRML03_NS, 'areaSource')
NRML03_COMPLEX_FAULT_SOURCE = etree.QName(NRML03_NS, 'complexFaultSource')
NRML03_SIMPLE_FAULT_SOURCE = etree.QName(NRML03_NS, 'simpleFaultSource')
NRML03_TECTONIC_REGION = etree.QName(NRML03_NS, 'tectonicRegion')
NRML03_RUPTURE_RATE_MODEL = etree.QName(NRML03_NS, 'ruptureRateModel')
NRML03_HYPOCENTRAL_DEPTH = etree.QName(NRML03_NS, 'hypocentralDepth')
NRML03_RAKE = etree.QName(NRML03_NS, 'rake')
NRML03_TGR = etree.QName(NRML03_NS, 'truncatedGutenbergRichter')
NRML03_EDI = etree.QName(NRML03_NS, 'evenlyDiscretizedIncrementalMFD')
NRML03_FAULT_TOP_EDGE = etree.QName(NRML03_NS, 'faultTopEdge')
NRML03_FAULT_BOTTOM_EDGE = etree.QName(NRML03_NS, 'faultBottomEdge')
NRML03_DIP = etree.QName(NRML03_NS, 'dip')
NRML03_UPPER_SEISMO_DEPTH = etree.QName(NRML03_NS, 'upperSeismogenicDepth')
NRML03_LOWER_SEISMO_DEPTH = etree.QName(NRML03_NS, 'lowerSeismogenicDepth')

def _parse_source_model_file(source_model_file):
    """
    Parse source model file in NRML 0.3.
    """
    parse_args = dict(source=source_model_file)

    srcs = []
    for _, element in etree.iterparse(**parse_args):
        if element.tag == NRML03_AREA_SOURCE.text:
            srcs.append(_parse_area_source(element))
        if element.tag == NRML03_COMPLEX_FAULT_SOURCE.text:
            srcs.append(_parse_complex_fault_source(element))
        if element.tag == NRML03_SIMPLE_FAULT_SOURCE.text:
            srcs.append(_parse_simple_fault_source(element))

    return srcs

def _parse_area_source(element):
    """
    Parse NRML 0.3 area source element.
    Note that the ruptureDepthDistribution element is neglected because
    it's not used in NRML 0.4 schema.
    """
    ID = element.get(gml.GML_ID.text)
    mfds_rakes = []
    for e in element.iter():
        if e.tag == gml.GML_NAME.text:
            name = e.text
        if e.tag == NRML03_TECTONIC_REGION.text:
            tect_reg = e.text
        if e.tag == gml.GML_POS_LIST.text:
            polygon = gml._get_polygon_from_2DLinestring(e.text)
        if e.tag == NRML03_RUPTURE_RATE_MODEL.text:
            mfds_rakes.append(_parse_rupture_rate_model(e))
        if e.tag == NRML03_HYPOCENTRAL_DEPTH:
            hypo_depth = e.text

    return AreaSourceNrml03(ID, name, tect_reg, polygon, mfds_rakes,
                            hypo_depth)

def _parse_complex_fault_source(element):
    """
    Parse NRML 0.3 complex fault source element.
    """
    ID = element.get(gml.GML_ID.text)
    for e in element.iter():
        if e.tag == gml.GML_NAME.text:
            name = e.text
        if e.tag == NRML03_TECTONIC_REGION.text:
            tect_reg = e.text
        if e.tag == NRML03_RAKE:
            rake = float(e.text)
        if e.tag == NRML03_TGR.text:
            mfd = _parse_truncated_gutenberg_richter(e)
        if e.tag == NRML03_EDI.text:
            mfd = _parse_incremental_mfd(e)
        if e.tag == NRML03_FAULT_TOP_EDGE.text:
            line_element = e.find('%s' % gml.GML_LINE_STRING)
            top_edge = gml._parse_3DLineString(line_element)
        if e.tag == NRML03_FAULT_BOTTOM_EDGE.text:
            line_element = e.find('%s' % gml.GML_LINE_STRING)
            bottom_edge = gml._parse_3DLineString(line_element)

    return ComplexFaultSourceNRML03(ID, name, tect_reg, mfd, top_edge,
                                    bottom_edge, rake)

def _parse_simple_fault_source(element):
    """
    Parse NRML 0.3 simple fault source element.
    """
    ID = element.get(gml.GML_ID.text)
    for e in element.iter():
        if e.tag == gml.GML_NAME.text:
            name = e.text
        if e.tag == NRML03_TECTONIC_REGION.text:
            tect_reg = e.text
        if e.tag == NRML03_RAKE:
            rake = float(e.text)
        if e.tag == NRML03_TGR.text:
            mfd = _parse_truncated_gutenberg_richter(e)
        if e.tag == NRML03_EDI.text:
            mfd = _parse_incremental_mfd(e)
        if e.tag == gml.GML_LINE_STRING.text:
            fault_trace = gml._parse_3DLineString(e)
        if e.tag == NRML03_DIP.text:
            dip = e.text
        if e.tag == NRML03_UPPER_SEISMO_DEPTH.text:
            upper_seismo_depth = e.text
        if e.tag == NRML03_LOWER_SEISMO_DEPTH.text:
            lower_seismo_depth = e.text

    return SimpleFaultSourceNRML03(ID, name, tect_reg, rake, mfd, fault_trace,
                                   dip, upper_seismo_depth, lower_seismo_depth)

def _parse_rupture_rate_model(element):
    """
    Parse NRML 0.3 rupture rate model. Return tuple consisting of mfd and rake
    angle.
    """
    for e in element.iter():
        if e.tag == NRML03_TGR.text:
            mfd = _parse_truncated_gutenberg_richter(e)
        if e.tag == NRML03_EDI.text:
            mfd = _parse_incremental_mfd(e)
        if e.tag == NRML03_RAKE.text:
            rake = e.text

    return (mfd, rake)

def _parse_incremental_mfd(element):
    """
    Parse NRML 0.3 evenly discretized incremental MFD.
    """
    min_mag = float(element.attrib['minVal'])
    bin_size = float(element.attrib['binSize'])
    rates = numpy.array(element.text.split(), dtype=float)

    return EvenlyDiscretizedIncrementalMfdNrml03(min_mag, bin_size, rates)

def _parse_truncated_gutenberg_richter(element):
    """
    Parse NRML truncated GR element, and returns maximum magnitude
    and total occurrence rate.
    """
    for e in element.iter():
        if e.tag == '%saValueCumulative' % NRML03:
            a_val = float(e.text)
        if e.tag == '%sbValue' % NRML03:
            b_val = float(e.text)
        if e.tag == '%sminMagnitude' % NRML03:
            min_mag = float(e.text)
        if e.tag == '%smaxMagnitude' % NRML03:
            max_mag = float(e.text)

    return TruncatedGutenbergRichterMfdNrml03(a_val, b_val, min_mag,
                                                  max_mag)

class EvenlyDiscretizedIncrementalMfdNrml03(object):
    """
    Class representing NRML 0.3 evenly discretized incremental MFD.
    """
    def __init__(self, min_mag, bin_size, rates):
        self.min_mag = min_mag
        self.bin_size = bin_size
        self.rates = rates

class TruncatedGutenbergRichterMfdNrml03(object):
    """
    Class representing NRML 0.3 truncated Gutenberg Richter MFD.
    """
    def __init__(self, a_val, b_val, min_mag, max_mag):
        self.a_val = a_val
        self.b_val = b_val
        self.min_mag = min_mag
        self.max_mag = max_mag

class AreaSourceNrml03(object):
    """
    Class representing NRML 0.3 area source.
    """
    def __init__(self, ID, name, tect_reg, polygon, mfds_rakes, hypo_depth):
        self.ID = ID
        self.name = name
        self.tect_reg = tect_reg
        self.polygon = polygon
        self.mfds_rakes = mfds_rakes
        self.hypo_depth = hypo_depth

class ComplexFaultSourceNRML03(object):
    """
    Class representing NRML 0.3 complex fault source.
    """
    def __init__(self, ID, name, tect_reg, mfd, top_edge, bottom_edge, rake):
        self.ID = ID
        self.name = name
        self.tect_reg = tect_reg
        self.mfd = mfd
        self.top_edge = top_edge
        self.bottom_edge = bottom_edge
        self.rake = rake

class SimpleFaultSourceNRML03(object):
    """
    Class representing NRML 0.3 simple fault source.
    """
    def __init__(self, ID, name, tect_reg, rake, mfd, fault_trace,
                 dip, upper_seismo_depth, lower_seismo_depth):
         self.ID = ID
         self.name = name
         self.tect_reg = tect_reg
         self.rake = float(rake)
         self.mfd = mfd
         self.dip = float(dip)
         self.upper_seismo_depth = float(upper_seismo_depth)
         self.lower_seismo_depth = float(lower_seismo_depth)
         self.fault_trace = self._correct_fault_trace(fault_trace)

    def _correct_fault_trace(self, fault_trace):
        """
        Shift fault trace to earth surface along dip direction.
        """
        # create NHLIB line
        fault_trace = [Point(lon, lat, depth) for lon, lat, depth in fault_trace]

        # compute fault trace azimuth
        azimuth = (fault_trace[0].azimuth(fault_trace[1]) + 270.0) % 360.0
        vertical_increment = -self.upper_seismo_depth
        horizontal_distance = self.upper_seismo_depth / \
                               numpy.tan(numpy.radians(self.dip))

        # recompute fault trace at the surface by shifting original
        # fault trace locations updip
        new_locs = []
        for p in fault_trace:
            loc = p.point_at(horizontal_distance, vertical_increment, azimuth)
            new_locs.append(loc)

        fault_trace = numpy.empty((0,3))
        for loc in new_locs:
            fault_trace = numpy.append(
                fault_trace,
                [[loc.longitude, loc.latitude, loc.depth]],
                axis=0)

        return fault_trace
    