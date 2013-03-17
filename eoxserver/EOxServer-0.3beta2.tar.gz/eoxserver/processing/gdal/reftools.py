#-------------------------------------------------------------------------------
# $Id: reftools.py 2294 2013-03-09 11:44:15Z meissls $
#
# Project: EOxServer <http://eoxserver.org>
# Authors: Stephan Krause <stephan.krause@eox.at>
#          Martin Paces <martin.paces@eox.at>
#
#-------------------------------------------------------------------------------
# Copyright (C) 2011 EOX IT Services GmbH
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell 
# copies of the Software, and to permit persons to whom the Software is 
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies of this Software or works derived from this Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#-------------------------------------------------------------------------------

from tempfile import mkstemp
import ctypes as C
import os.path
import logging

from eoxserver.contrib import gdal
from eoxserver.core.util.bbox import BBox
from eoxserver.core.exceptions import InternalError


logger = logging.getLogger(__name__)

class RECT(C.Structure):
    _fields_ = [("x_off", C.c_int),
                ("y_off", C.c_int),
                ("x_size", C.c_int),
                ("y_size", C.c_int)]


class SUBSET(C.Structure):
    _fields_ = [("srid", C.c_int),
                ("minx", C.c_double),
                ("miny", C.c_double),
                ("maxx", C.c_double),
                ("maxy", C.c_double)]


class IMAGE_INFO(C.Structure):
    _fields_ = [("x_size", C.c_size_t),
                ("y_size", C.c_size_t),
                ("geotransform", C.ARRAY(C.c_double, 6))]


_lib_path = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "_reftools.so"
)

global REFTOOLS_USEABLE
    
try:
    _lib = C.LibraryLoader(C.CDLL).LoadLibrary(_lib_path)

    _get_footprint_wkt = _lib.eoxs_get_footprint_wkt
    _get_footprint_wkt.argtypes = [C.c_void_p, C.c_int, C.POINTER(C.c_char_p)]
    _get_footprint_wkt.restype = C.c_int

    _rect_from_subset = _lib.eoxs_rect_from_subset
    _rect_from_subset.argtypes = [C.c_void_p, C.POINTER(SUBSET), C.c_int, C.POINTER(RECT)]
    _rect_from_subset.restype = C.c_int

    _create_rectified_vrt = _lib.eoxs_create_rectified_vrt
    _create_rectified_vrt.argtypes = [C.c_void_p, C.c_char_p, C.c_int]
    _create_rectified_vrt.restype = C.c_int

    _suggested_warp_output = _lib.eoxs_suggested_warp_output
    _suggested_warp_output.argtypes = [C.c_void_p, C.c_char_p, C.c_char_p, C.c_int, C.POINTER(IMAGE_INFO)]
    _suggested_warp_output.restype = C.c_int

    _reproject_image = _lib.eoxs_reproject_image
    _reproject_image.argtypes = [C.c_void_p, C.c_char_p, C.c_void_p, C.c_char_p, C.c_int, C.c_double, C.c_double, C.c_int]
    _reproject_image.restype = C.c_int

    _free_string = _lib.eoxs_free_string
    _free_string.argtypes = [C.c_char_p]

    REFTOOLS_USABLE = True
except:
    logger.warn("Could not load '%s'. Referenceable Datasets will not be usable." % _lib_path)
    
    REFTOOLS_USABLE = False


def _open_ds(path_or_ds):
    if isinstance(path_or_ds, basestring):
        gdal.AllRegister()
        return gdal.Open(str(path_or_ds))
    return path_or_ds


def requires_reftools(func):
    """ Decorator function that checks whether or not the reftools library is 
        available and raises if not.
    """
    
    def wrapped(*args, **kwargs):
        if not REFTOOLS_USABLE:
            raise InternalError("Referenceable grid handling is disabled! "
                                "Did you compile the 'reftools' C module?!")
        return func(*args, **kwargs)
    
    return wrapped


@requires_reftools
def get_footprint_wkt(path_or_ds, order=0):
    """ Use -1 for TPS, 0 for automatic order, 1, 2 for order 1, 2 in GCP
    """
    
    ds = _open_ds(path_or_ds)
    
    result = C.c_char_p()
    
    ret = _get_footprint_wkt(C.c_void_p(long(ds.this)), order, C.byref(result))
    if ret != gdal.CE_None:
        raise RuntimeError(gdal.GetLastErrorMsg())
    
    string = C.cast(result, C.c_char_p).value
    
    _free_string(result)
    return string

@requires_reftools
def rect_from_subset(path_or_ds, srid, minx, miny, maxx, maxy, order=0):
    
    ds = _open_ds(path_or_ds)
    
    rect = RECT()
    ret = _rect_from_subset(
        C.c_void_p(long(ds.this)),
        C.byref(SUBSET(srid, minx, miny, maxx, maxy)),
        order,
        C.byref(rect)
    )
    if ret != gdal.CE_None:
        raise RuntimeError(gdal.GetLastErrorMsg())
    
    return BBox(rect.x_size, rect.y_size, rect.x_off, rect.y_off)


@requires_reftools
def create_rectified_vrt(path_or_ds, vrt_path, srid=None):
    ds = _open_ds(path_or_ds)
    ptr = C.c_void_p(long(ds.this))

    if srid:
        ret = _create_rectified_vrt(ptr, vrt_path, srid)
    else:
        ret = _create_rectified_vrt(ptr, vrt_path, 0)  
    
    if ret != gdal.CE_None:
        raise RuntimeError(gdal.GetLastErrorMsg())


@requires_reftools
def create_temporary_vrt(path_or_ds, srid=None):
    try:
        from eoxserver.core.system import System
        vrt_tmp_dir = System.getConfig().getConfigValue("processing.gdal.reftools", "vrt_tmp_dir")
    except: vrt_tmp_dir = None
    
    _, vrt_path = mkstemp(
        dir = vrt_tmp_dir,
        suffix = ".vrt"
    )
    
    create_rectified_vrt(path_or_ds, vrt_path, srid)
    
    return vrt_path


@requires_reftools
def suggested_warp_output(path_or_ds, src_wkt, dst_wkt, order=0):
    ds = _open_ds(path_or_ds)
    ptr = C.c_void_p(long(ds.this))
    info = IMAGE_INFO()
    
    ret = _suggested_warp_output(
        ptr,
        src_wkt,
        dst_wkt,
        order,
        C.byref(info)
    )
    
    if ret != gdal.CE_None:
        raise RuntimeError(gdal.GetLastErrorMsg())
    
    return info.x_size, info.y_size, info.geotransform
    
@requires_reftools
def reproject_image(src_ds, src_wkt, dst_ds, dst_wkt, resample=gdal.GRA_NearestNeighbour, memory_limit=0.0, max_error=0.0, order=0): 
    
    ret = _reproject_image(
        C.c_void_p(long(src_ds.this)),
        src_wkt,
        C.c_void_p(long(dst_ds.this)),
        dst_wkt,
        resample,
        memory_limit,
        max_error,
        order
    )
    
    if ret != gdal.CE_None:
        raise RuntimeError(gdal.GetLastErrorMsg())
