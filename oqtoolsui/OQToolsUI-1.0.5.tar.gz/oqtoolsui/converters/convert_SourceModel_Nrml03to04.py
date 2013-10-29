"""
Script converting source model file from NRML03 to NRML04.
"""
from lxml import etree
import csv
from decimal import Decimal

from oqtoolsui.converters import gml
from oqtoolsui.converters import nrml03


#FAULTING_STYLE_FILE = 'converters/faulting_style_data.csv'
from oqtoolsui.converters import nrml04

FAULTING_STYLE_FILE = '/home/orhan/Desktop/EMME_AsModel_ver2_2_brc1.csv'
SOURCE_MODEL_NAME = 'SHARE ASC Area Source Model'
#STRIKES_WEIGHTS = [(0.0, Decimal('0.5')), (90.0, Decimal('0.5'))]
STRIKES_WEIGHTS = [(0.0, Decimal('1.0'))]
DIP = 90.0
UPPER_SEISMO_DEPTH = 0.0
LOWER_SEISMO_DEPTH =40.0
MAG_SCALE_REL = 'WC1994'
RUPT_ASPECT_RATIO = 1.0




    
def _read_faulting_style_file():
    """
    Read faulting style file and returns dictionary where the keys
    are the sources IDs, and for each ID a tuple containing strike and
    dip values are stored.
    """
    csvfile = open(FAULTING_STYLE_FILE, 'rU')
    reader = csv.reader(csvfile)
    strikes_dips = {}
    for row in reader:
        strikes_dips[row[0]] = (row[1], row[2])
    return strikes_dips

def _write_source_model_file_nrml04(file_name, srcs, strikes_dips):
    """
    Dump source data (coming from NRML 0.3 file - srcs) in NRML 0.4 file.
    For each ruptureRateModel in a NRML 0.3 areaSource a corresponding
    NRML 0.4 areaSource is created. The nodal plane distribution contains
    only one nodal plane with the original rake value, while strike and dip
    values are overridden by default values given in the script (STRIKE, DIP).
    """
    nrml = nrml04._create_nrml()

    source_model = nrml04._append_source_model(nrml, SOURCE_MODEL_NAME)

    src_idx = [0]
    for src in srcs:
        if isinstance(src, nrml03.AreaSourceNrml03):
            _append_area_source(source_model, src, src_idx, strikes_dips)

        if isinstance(src, nrml03.ComplexFaultSourceNRML03):
            _append_complex_fault_source(source_model, src, src_idx)

        if isinstance(src, nrml03.SimpleFaultSourceNRML03):
            _append_simple_fault_source(source_model, src, src_idx)

    # write to file
    f = open(file_name,'w')
    f.write(etree.tostring(nrml, pretty_print=True, xml_declaration=True,
                           encoding="UTF-8"))
    f.close()

def _append_area_source(source_model, src, src_idx, strikes_dips):
    """
    Append area source.
    """
    for mfd, rake in src.mfds_rakes:
        src_idx[0] += 1

        area_source = nrml04._append_id_name_tect_reg(source_model,
                                               nrml04.NRML04_AREA_SOURCE,
                                               str(src_idx[0]),
                                               src.name,
                                               src.tect_reg)

        area_geometry = nrml04._append_geometry(area_source,
                                         nrml04.NRML04_AREA_GEOMETRY) 

        gml._append_polygon(area_geometry, src.polygon)

        nrml04._append_upper_seismo_depth(area_geometry,
                                   str(UPPER_SEISMO_DEPTH))

        nrml04._append_lower_seismo_depth(area_geometry,
                                   str(LOWER_SEISMO_DEPTH))

        nrml04._append_mag_scaling_rel(area_source, MAG_SCALE_REL)

        nrml04._append_rupt_aspect_ratio(area_source,
                                         str(RUPT_ASPECT_RATIO))

        if isinstance(mfd, nrml03.EvenlyDiscretizedIncrementalMfdNrml03):
            nrml04._append_incremental_mfd(area_source, mfd)

        if isinstance(mfd, nrml03.TruncatedGutenbergRichterMfdNrml03):
            nrml04._append_truncated_gr_mfd(area_source, mfd)

        # check if in the source a strike and dip values are provided
        ID = src.ID.split('_')[0]
        if ID in strikes_dips:
            print 'Strike and dip values defined for source %s' % ID
            strike, dip = strikes_dips[ID]
            nrml04._append_nodal_plane_dist(area_source, [(strike, Decimal('1.0'))],
                                            dip, rake)
        else:
            print 'Source %s has default strikes and dip values' % src.ID                                    
            nrml04._append_nodal_plane_dist(area_source, STRIKES_WEIGHTS,
                                        DIP, rake)

        nrml04._append_hypo_depth_dist(area_source, src.hypo_depth)

def _append_complex_fault_source(source_model, src, src_idx):
    """
    Append complex fault source.
    """
    src_idx[0] += 1
    complex_source = nrml04._append_id_name_tect_reg(source_model,
                                           nrml04.NRML04_COMPLEX_FAULT_SOURCE,
                                           str(src_idx[0]),
                                           src.name,
                                           src.tect_reg)

    complex_geometry = nrml04._append_geometry(complex_source,
        nrml04.NRML04_COMPLEX_FAUL_GEOMETRY)

    fault_top_edge = etree.Element(nrml04.NRML04_FAULT_TOP_EDGE)
    complex_geometry.append(fault_top_edge)

    gml._append_3DLineString(fault_top_edge, src.top_edge)

    fault_bottom_edge = etree.Element(nrml04.NRML04_FAULT_BOTTOM_EDGE)
    complex_geometry.append(fault_bottom_edge)

    gml._append_3DLineString(fault_bottom_edge, src.bottom_edge)

    nrml04._append_mag_scaling_rel(complex_source, MAG_SCALE_REL)

    nrml04._append_rupt_aspect_ratio(complex_source,
                                     str(RUPT_ASPECT_RATIO))

    if isinstance(src.mfd, nrml03.EvenlyDiscretizedIncrementalMfdNrml03):
        nrml04._append_incremental_mfd(complex_source, src.mfd)

    if isinstance(src.mfd, nrml03.TruncatedGutenbergRichterMfdNrml03):
        nrml04._append_truncated_gr_mfd(complex_source, src.mfd)

    nrml04._append_rake(complex_source, src.rake)

def _append_simple_fault_source(source_model, src, src_idx):
    """
    Append complex fault source.
    """
    src_idx[0] += 1
    simple_source = nrml04._append_id_name_tect_reg(source_model,
                                           nrml04.NRML04_SIMPLE_FAULT_SOURCE,
                                           str(src_idx[0]),
                                           src.name,
                                           src.tect_reg)

    simple_geometry = nrml04._append_geometry(simple_source,
        nrml04.NRML04_SIMPLE_FAULT_GEOMETRY)

    gml._append_2DLineString(simple_geometry, src.fault_trace)
    
    nrml04._append_dip(simple_geometry, src.dip)

    nrml04._append_upper_seismo_depth(simple_geometry, src.upper_seismo_depth)

    nrml04._append_lower_seismo_depth(simple_geometry, src.lower_seismo_depth)

    nrml04._append_mag_scaling_rel(simple_source, MAG_SCALE_REL)

    nrml04._append_rupt_aspect_ratio(simple_source,
                                     str(RUPT_ASPECT_RATIO))

    if isinstance(src.mfd, nrml03.EvenlyDiscretizedIncrementalMfdNrml03):
        nrml04._append_incremental_mfd(simple_source, src.mfd)

    if isinstance(src.mfd, nrml03.TruncatedGutenbergRichterMfdNrml03):
        nrml04._append_truncated_gr_mfd(simple_source, src.mfd)

    nrml04._append_rake(simple_source, src.rake)

def convertv3Tov4(source, target):
    strikes_dips = _read_faulting_style_file()
    srcs =  nrml03._parse_source_model_file(source)
    _write_source_model_file_nrml04(target, srcs, strikes_dips)

if __name__=='__main__':
    convertv3Tov4('/home/orhan/Desktop/EMME_ASMODEL_BRANCH01.xml', '/home/orhan/Desktop/EMME_ASMODEL_BRANCH01_4.xml')