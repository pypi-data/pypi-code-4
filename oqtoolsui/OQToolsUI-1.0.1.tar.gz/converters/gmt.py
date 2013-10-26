"""
Module containing utilities for plotting with GMT.
"""
from converters import source_model
from converters import nrml04
from math import sin, cos, radians, degrees, atan2
from subprocess import call
import numpy

MAP_WIDTH = 10.0
FRAME_ANNOTATION_SPACING = 10.0
CPT_INCREMENT = 0.01
POINT_SIZE = 0.05

def _plot_area_srcs_polygons(src_model, projection_type, plot_file):
    """
    Plot area sources polygons.
    """
    areas = source_model._get_area_sources(src_model)
    polygon_file = _save_polygon_coords(areas)

    reg, proj, annot = _create_base_map_for_source_model(src_model, 
                                                         projection_type,
                                                         plot_file)

    _plot_area_source_polygons(reg, proj, polygon_file.name, plot_file)

    _plot_coast_line(reg, proj, plot_file)

def _plot_area_source_polygons(reg, proj, polygon_file, plot_file):
    """
    Plot area source polygons.
    """
    call(["psxy", polygon_file, reg, proj,"-M", "-N", "-O", "-K"], stdout=plot_file)

def _save_polygon_coords(areas):
    """
    Save polygon coordinates from area sources to ASCII file to be read
    by GMT.
    Return file object.
    """
    polygons = open('polygons.dat', 'w')
    for area in areas:
        polygon = area.polygon
        polygons.write('> \n')
        for lon, lat in polygon:
            polygons.write('%s %s\n' % (lon, lat))
        polygons.write('%s %s\n' % (polygon[0,0], polygon[0,1]))
    polygons.close()

    return polygons

def _plot_point_srcs_occ_rates(src_model, projection_type, plot_file):
    """
    Plot point sources and their occurrence rates.
    """
    locs_rates = source_model._get_point_sources_occ_rates(src_model)
    numpy.savetxt('locs_rates.dat', locs_rates)
    cpt_file = _create_color_scale(numpy.min(locs_rates[:,2]),
                                   numpy.max(locs_rates[:,2]))

    reg, proj, annot = _create_base_map_for_source_model(src_model, 
                                                         projection_type,
                                                         plot_file)
    _plot_point_source_data(reg, proj, 'locs_rates.dat', cpt_file.name,
                            plot_file)
    _plot_coast_line(reg, proj, plot_file)

def _plot_point_source_data(reg, proj, points_data_file, cpt_file, plot_file):
    """
    Plot point source data coming in a 2D matrix. The third column
    represents the data to be plotted.
    """
    call(["psxy", points_data_file, reg, proj, "-C%s" % cpt_file,
          "-Sp%s" % POINT_SIZE, "-N", "-O", "-K"], stdout=plot_file)

def _create_base_map_for_source_model(src_model, projection_type, plot_file):
    """
    Create GMT base map.
    """
    bb = _get_source_model_bounding_box(src_model)
    region = "-R%s/%s/%s/%s" % (bb[0], bb[1], bb[2], bb[3])
    annotation = "-B%s/%s" % (FRAME_ANNOTATION_SPACING, FRAME_ANNOTATION_SPACING)

    if projection_type == 'Equidistant Conic':
        lon_0, lat_0, lat_1, lat_2 = _get_equidistant_conic_params(bb)
        projection = "-JB%s/%s/%s/%s/%s" % (lon_0, lat_0, lat_1, lat_2, MAP_WIDTH)
    else:
        raise ValueError('Projection type %s not recognized' % projection_type)

    call(["psbasemap",region, projection, annotation,"-Bg2:ws:", "-Xc", "-Yc", "-K"],
          stdout=plot_file)

    return region, projection, annotation

def _plot_coast_line(reg, proj, plot_file):
    """
    Plot coast lines.
    """
    call(["pscoast", reg, proj, "-Wthin", "-N1", "-A1000",
          "-O"],stdout=plot_file)

def _create_color_scale(min_value, max_value):
    """
    Create color scale for given min and max values
    """
    cpt_file = open('data.cpt', 'w')
    colorscale = "-T%s/%s/%s" % (min_value, max_value, CPT_INCREMENT)
    call(["makecpt","-Cjet",colorscale,"-D"],stdout=cpt_file)

    return cpt_file


def _get_equidistant_conic_params(bb):
    """
    Get equidistant conic params from bounding box.
    """
    lon_0 = degrees(atan2((sin(radians(bb[0])) + sin(radians(bb[1]))) / 2,
                          (cos(radians(bb[0])) + cos(radians(bb[1]))) / 2))
    lat_0 = (bb[2] + bb[3]) / 2
    lat_1 = bb[2]
    lat_2 = bb[3]

    return lon_0, lat_0, lat_1, lat_2

def _get_source_model_bounding_box(src_model):
    """
    Extract bounding box for source model.
    """
    lons = []
    lats = []
    for src in src_model:
        if isinstance(src, nrml04.PointSourceNRML04):
            lons.append(src.lon)
            lats.append(src.lat)
        if isinstance(src, nrml04.AreaSourceNRML04):
            for lon, lat in src.polygon:
                lons.append(lon)
                lats.append(lat)

    if len(lons) == 0:
        raise ValueError('No bounding box for the given source model.')

    bb = _get_bounding_box(lons, lats)

    return bb

def _get_bounding_box(lons, lats):
    """
    Extract bounding box for the given coordinates.
    """
    min_lon = min(lons)
    max_lon = max(lons)
    min_lat = min(lats)
    max_lat = max(lats)
    # a segment crosses the international date line if the end positions
    # have different sign and they are more than 180 degrees longitude
    # apart
    if min_lon < 0 and max_lon > 0 and (max_lon - min_lon) > 180:
        lons = numpy.array(lons)
        idx_west = numpy.where(lons <= 0)
        idx_est = numpy.where(lons > 0)
        min_lon = numpy.max(lons[idx_west])
        max_lon = numpy.min(lons[idx_est])
        return (max_lon, 180 + abs(-180 - min_lon), min_lat, max_lat)
    else:
        return (min_lon, max_lon, min_lat, max_lat)
    
    