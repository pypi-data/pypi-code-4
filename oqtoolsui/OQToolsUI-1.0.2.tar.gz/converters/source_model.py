"""
Module containing methods for processing source model data (as list of NRML04
sources)
"""
import numpy
from converters import nrml04

def _get_point_sources(src_model):
    """
    Extract point sources from a source model.
    """
    points = []
    for src in src_model:
        if isinstance(src, nrml04.PointSourceNRML04):
            points.append(src)

    return points

def _get_area_sources(src_model):
    """
    Extract area sources from a source model.
    """
    areas = []
    for src in src_model:
        if isinstance(src, nrml04.AreaSourceNRML04):
            areas.append(src)

    return areas

def _get_point_sources_occ_rates(src_model):
    """
    Return point sources locations with their occurrence rates.
    Everything is returned as a 2D numpy array.
    """
    points = _get_point_sources(src_model)
    points_data = []
    for p in points:
        points_data.append([p.lon, p.lat, p.mfd.get_tot_occ_rate()])

    return numpy.array(points_data)