"""
Module containing NRML 0.4 constants and utility methods.
"""
from lxml import etree
import numpy
from oqtoolsui.converters import gml

NRML04_NS = 'http://openquake.org/xmlns/nrml/0.4'
NRML04 = "{%s}" % NRML04_NS
NRML04_ROOT_TAG = '%snrml' % NRML04
NRML04_SOURCE_MODEL = etree.QName(NRML04_NS,'sourceModel')
NRML04_AREA_SOURCE = etree.QName(NRML04_NS,'areaSource')
NRML04_POINT_SOURCE = etree.QName(NRML04_NS,'pointSource')
NRML04_COMPLEX_FAULT_SOURCE = etree.QName(NRML04_NS, 'complexFaultSource')
NRML04_SIMPLE_FAULT_SOURCE = etree.QName(NRML04_NS, 'simpleFaultSource')
NRML04_AREA_GEOMETRY = etree.QName(NRML04_NS,'areaGeometry')
NRML04_POINT_GEOMETRY = etree.QName(NRML04_NS, 'pointGeometry')
NRML04_UPPER_SEISMO_DEPTH = etree.QName(NRML04_NS,'upperSeismoDepth')
NRML04_LOWER_SEISMO_DEPTH = etree.QName(NRML04_NS,'lowerSeismoDepth')
NRML04_MAG_SCALE_REL = etree.QName(NRML04_NS,'magScaleRel')
NRML04_RUPT_ASPECT_RATIO = etree.QName(NRML04_NS,'ruptAspectRatio')
NRML04_INCREMENTAL_MFD = etree.QName(NRML04_NS,'incrementalMFD')
NRML04_TRUNCATED_GR = etree.QName(NRML04_NS,'truncGutenbergRichterMFD')
NRML04_OCCUR_RATES = etree.QName(NRML04_NS,'occurRates')
NRML04_NODAL_PLANE_DIST = etree.QName(NRML04_NS,'nodalPlaneDist')
NRML04_NODAL_PLANE = etree.QName(NRML04_NS,'nodalPlane')
NRML04_HYPO_DEPTH_DIST = etree.QName(NRML04_NS,'hypoDepthDist')
NRML04_HYPO_DEPTH = etree.QName(NRML04_NS,'hypoDepth')
NRML04_COMPLEX_FAUL_GEOMETRY = etree.QName(NRML04_NS, 'complexFaultGeometry')
NRML04_FAULT_TOP_EDGE = etree.QName(NRML04_NS, 'faultTopEdge')
NRML04_FAULT_BOTTOM_EDGE = etree.QName(NRML04_NS, 'faultBottomEdge')
NRML04_RAKE = etree.QName(NRML04_NS, 'rake')
NRML04_SIMPLE_FAULT_GEOMETRY = etree.QName(NRML04_NS, 'simpleFaultGeometry')
NRML04_DIP = etree.QName(NRML04_NS, 'dip')
NSMAP = {None: NRML04_NS, "gml": gml.GML_NS}

def _parse_source_model_file(source_model_file):
    """
    Parse source model file in NRML 0.4.
    """
    parse_args = dict(source=source_model_file)

    srcs = []
    for _, element in etree.iterparse(**parse_args):
        if element.tag == NRML04_POINT_SOURCE.text:
            srcs.append(_parse_point_source(element))
        if element.tag == NRML04_AREA_SOURCE.text:
            srcs.append(_parse_area_source(element))

    return srcs

def _parse_area_source(element):
    """
    Parse NRML 0.4 area source element.
    """
    ID, name, tect_reg = _get_id_name_tect_reg(element)

    polygon = _get_polygon(element)

    mfd = _get_mfd(element)

    return AreaSourceNRML04(polygon, mfd)

def _get_polygon(element):
    """
    Return polygon coordinates from area source element.
    """
    polygon =  element.find('%s/%s/%s/%s/%s' %
                           (NRML04_AREA_GEOMETRY, gml.GML_POLYGON,
                            gml.GML_EXTERIOR, gml.GML_LINEAR_RING,
                            gml.GML_POS_LIST)).text

    polygon = gml._get_polygon_from_2DLinestring(polygon)

    return polygon
    

def _parse_point_source(element):
    """
    Parse NRML 0.4 point source element.
    """
    ID, name, tect_reg = _get_id_name_tect_reg(element)

    lon, lat = _get_point_source_location(element)

    mfd = _get_mfd(element)

    return PointSourceNRML04(lon, lat, mfd)

def _get_id_name_tect_reg(element):
    """
    Return id, name, and tectonic region of a source element.
    """
    ID = element.attrib['id']
    name =  element.attrib['name']
    tect_reg = element.attrib['tectonicRegion']

    return ID, name, tect_reg

def _get_point_source_location(element):
    """
    Return point source location (lon, lat).
    """
    pos = element.find('%s/%s/%s' %
                       (NRML04_POINT_GEOMETRY, gml.GML_POINT, gml.GML_POS))
    pos = pos.text.split()

    return float(pos[0]), float(pos[1])

def _get_mfd(element):
    """
    Get mfd from source element.
    """
    mfd = element.find(NRML04_TRUNCATED_GR)
    if mfd is None:
        mfd = element.find(NRML04_INCREMENTAL_MFD)

    if mfd.tag == NRML04_TRUNCATED_GR:
        return TruncatedGRMfdNRML04(float(mfd.attrib['aValue']),
                                    float(mfd.attrib['bValue']),
                                    float(mfd.attrib['minMag']),
                                    float(mfd.attrib['maxMag']))
    elif mfd.tag == NRML04_INCREMENTAL_MFD:
        min_mag = float(mfd.attrib['minMag'])
        bin_width = float(mfd.attrib['binWidth'])
        occur_rates = numpy.array(mfd.find(NRML04_OCCUR_RATES.text).
                                  text.split(), dtype=float)
        return IncrementalMfdNRML04(min_mag, bin_width, occur_rates)
    else:
        raise ValueError('MFD element nor recognized.')

def _create_nrml():
    """
    Create and return NRML 0.4 root element.
    """
    return etree.Element(NRML04_ROOT_TAG, nsmap=NSMAP)

def _append_source_model(element, name):
    """
    Append and return NRML 0.4 source model element.
    """
    attrib = {'name': name}
    source_model = etree.Element(NRML04_SOURCE_MODEL,attrib=attrib)
    element.append(source_model)
    return source_model

def _append_id_name_tect_reg(element, NRML04_SOURCE, ID, name, tect_reg):
    """
    Append id, name, tectonic region type for the given NRML 0.4 source
    typology.

    Returns the source element.
    """
    attrib = {'id': ID, 'name': name, 'tectonicRegion': tect_reg}
    source = etree.Element(NRML04_SOURCE, attrib=attrib)
    element.append(source)

    return source

def _append_geometry(element, NRML04_GEOMETRY):
    """
    Append NRML 0.4 geometry to element and return the geometry element.
    """
    geometry = etree.Element(NRML04_GEOMETRY)
    element.append(geometry)

    return geometry

def _append_dip(element, dip_value):
    """
    Append NRML 0.4 dip element.
    """
    dip = etree.Element(NRML04_DIP)
    dip.text = str(dip_value)
    element.append(dip)

def _append_upper_seismo_depth(element, upper_seismo_depth):
    """
    Append NRML 0.4 upper seismogenic depth element.
    """
    usd = etree.Element(NRML04_UPPER_SEISMO_DEPTH)
    usd.text = str(upper_seismo_depth)
    element.append(usd)

def _append_lower_seismo_depth(element, lower_seismo_depth):
    """
    Append NRML 0.4 lower seismogenic depth element.
    """
    lsd = etree.Element(NRML04_LOWER_SEISMO_DEPTH)
    lsd.text = str(lower_seismo_depth)
    element.append(lsd)

def _append_mag_scaling_rel(element, mag_scale_rel):
    """
    Append NRML 0.4 magnitude scaling relationship element.
    """
    msr = etree.Element(NRML04_MAG_SCALE_REL)
    msr.text = mag_scale_rel
    element.append(msr)

def _append_rupt_aspect_ratio(element, rupt_aspect_ratio):
    """
    Append NRML 0.4 rupture aspect ratio.
    """
    rar = etree.Element(NRML04_RUPT_ASPECT_RATIO)
    rar.text = str(rupt_aspect_ratio)
    element.append(rar)

def _append_incremental_mfd(element, mfd):
    """
    Append NRML 0.4 incremental MFD.
    mfd is an instance of class EvenlyDiscretizedIncrementalMfdNrml03.
    """
    attrib = {'minMag': str(mfd.min_mag),
              'binWidth': str(mfd.bin_size)}
    incremental_mfd = etree.Element(NRML04_INCREMENTAL_MFD,
                                    attrib=attrib)
    occur_rates = etree.Element(NRML04_OCCUR_RATES)
    occur_rates.text = ' '.join(str(v) for v in mfd.rates)
    incremental_mfd.append(occur_rates)
    element.append(incremental_mfd)

def _append_truncated_gr_mfd(element, mfd):
    """
    Append NRML 0.4 truncated GR MFD.
    mfd is an instance of TruncatedGutenbergRichterMfdNrml03.
    """
    attrib = {'aValue': str(mfd.a_val),
              'bValue': str(mfd.b_val),
              'minMag': str(mfd.min_mag),
              'maxMag': str(mfd.max_mag)}
    truncated_gr = etree.Element(NRML04_TRUNCATED_GR,
                                 attrib=attrib)
    element.append(truncated_gr)

def _append_nodal_plane_dist(element, strikes_weights, dip, rake):
    """
    Append NRML 0.4 nodal plane distribution for a set of strikes values (each
    with its own weight). Dip and rake are the same for all values.
    """
    nodal_plane_dist = etree.Element(NRML04_NODAL_PLANE_DIST)

    for strike, weight in strikes_weights:
        attrib = {'probability': str(weight), 'strike': str(strike),
                  'dip': str(dip), 'rake': str(rake)}
        nodal_plane = etree.Element(NRML04_NODAL_PLANE, attrib=attrib)
        nodal_plane_dist.append(nodal_plane)

    element.append(nodal_plane_dist)

def _append_hypo_depth_dist(element, hypo_depth):
    """
    Append NMRL 0.4 hypocentral depth distribution.
    """
    attrib = {'probability': '1.0', 'depth': hypo_depth}
    hypo_depth = etree.Element(NRML04_HYPO_DEPTH, attrib=attrib)
    hypo_depth_dist = etree.Element(NRML04_HYPO_DEPTH_DIST)
    hypo_depth_dist.append(hypo_depth)
    element.append(hypo_depth_dist)

def _append_rake(element, rake_value):
    """
    Append NRML 0.4 rake value
    """
    rake = etree.Element(NRML04_RAKE)
    rake.text = str(rake_value)
    element.append(rake)


class TruncatedGRMfdNRML04(object):
    """
    Class representing Truncated GR mfd in NRML 0.4
    """
    def __init__(self, a_value, b_value, min_mag, max_mag):
        self.a_value = a_value
        self.b_value = b_value
        self.min_mag = min_mag
        self.max_mag = max_mag

    def get_tot_occ_rate(self):
        """
        Compute total occurrence rate from Mmin and Mmax
        """
        return 10 ** (self.a_value - self.b_value * self.min_mag) - \
               10 ** (self.a_value - self.b_value * self.max_mag)


class IncrementalMfdNRML04(object):
    """
    Class representing Incremental mfd in NRML 0.4
    """
    def __init__(self, min_mag, bin_width, occur_rates):
        self.min_mag = min_mag
        self.bin_width = bin_width
        self.occur_rates = occur_rates

    def get_tot_occ_rate(self):
        """
        Compute total occurrence rate from Mmin and Mmax
        """
        return numpy.sum(self.occur_rates)

class AreaSourceNRML04(object):
    """
    Class representing area source in NRML 0.4.
    """
    def __init__(self, polygon, mfd):
        self.polygon = polygon
        self.mfd = mfd

class PointSourceNRML04(object):
    """
    Class representing point source in NRML 0.4.
    """
    def __init__(self, lon, lat, mfd):
        self.lon = lon
        self.lat = lat
        self.mfd = mfd