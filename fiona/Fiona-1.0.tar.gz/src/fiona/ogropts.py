"""
A module of functions that map Python Collection constructor kwargs to
OGR layer creation options.
"""

def shape_type(val):
    """Override the type of ESRI Shapefile created.

    For drivers: ESRI Shapefile.
    
    The value of ``val`` can be one of 'NULL' for a simple .dbf file
    with no .shp file, 'POINT', 'ARC', 'POLYGON' or 'MULTIPOINT' for 2D,
    or 'POINTZ', 'ARCZ', 'POLYGONZ' or 'MULTIPOINTZ' for 3D. Shapefiles
    with measure values are not supported, nor are MULTIPATCH files.
    """

    return "SHPT=" + val.upper()

