#!/usr/bin/env python2

'''Read and write image and video files with OpenCV'''


from cv2 import cv
from numpy import asarray, empty as _empty
from numpy import float32, float64
from numpy import int8, int16, int32, int64
from numpy import uint8, uint16, uint32, uint64
from os.path import exists as _exists

from . import utils


# Map of OpenCV image depths to NumPy array types
_cv_depths = {
    cv.IPL_DEPTH_8U:    'uint8',
    cv.IPL_DEPTH_8S:    'int8',
    cv.IPL_DEPTH_16U:   'uint16',
    cv.IPL_DEPTH_16S:   'int16',
    cv.IPL_DEPTH_32S:   'int32',
    cv.IPL_DEPTH_32F:   'float32',
    cv.IPL_DEPTH_64F:   'float64',
}


# Map of NumPy array type strings to types
_np_dtypes = {
    'int8':     int8,
    'int16':    int16,
    'int32':    int32,
    'int64':    int64,
    'uint8':    uint8,
    'uint16':   uint16,
    'uint32':   uint32,
    'uint64':   uint64,
    'float32':  float32,
    'float64':  float64,
}


# Inverse mapping of the above
_cv_depths_inv = dict((v, k) for k, v in _cv_depths.iteritems())


# Map of colours to array indices
RGB = {
    'B': 0,
    'G': 1,
    'R': 2,
}


def _template_image(image, depth):
    '''Return an empty image object of the same dimensions,
    colour depth, and number of channels as the given image.
    '''
    size = (image.width, image.height)
    channels = image.nChannels
    dup = cv.CreateImage(size, depth, channels)
    return dup


DEFAULT_IMAGE_FILE_EXT = '.png'


def _save_image(image, file, file_ext=None, random=False):
    '''Save an image object and return the file name.

    The parameter 'file_ext' specifies the file extension and
    format of the saved image.

    If the parameter 'random' is True, use a random file name.
    '''
    if not file_ext:
        file_ext = DEFAULT_IMAGE_FILE_EXT
    if random:
        newfile = utils.rand_filename(file, ext=file_ext)
    else:
        newfile = file
    newimage = _template_image(image, cv.IPL_DEPTH_8U)
    cv.ConvertScaleAbs(image, newimage, scale=255)
    cv.SaveImage(newfile, newimage)
    return newfile


def num_frames(video_file):
    '''Return the number of frames in a video file.
    '''
    cap = cv.CaptureFromFile(video_file)
    if not cap:
        raise IOError('CaptureFromFile')
    n = cv.GetCaptureProperty(cap, cv.CV_CAP_PROP_FRAME_COUNT)
    return int(n)


def _cv_to_array(im, dtype=None):
    '''Return an OpenCV image object as a NumPy array.

    If a dtype is specified, return an array of that type.
    '''
    arr_data = im[:, :]
    arr_shape = (im.height, im.width, im.nChannels)
    arr_dtype = _np_dtypes[_cv_depths[im.depth]]
    arr = asarray(arr_data, dtype=arr_dtype)
    arr.shape = arr_shape
    if not dtype:
        return arr
    new_arr = _empty(arr.shape, dtype=dtype)
    new_arr = arr.astype(_np_dtypes[dtype])
    return new_arr


def _array_to_cv(arr):
    '''Return a NumPy array as an OpenCV image object.
    '''
    im_channels = utils.n_channels(arr)
    swap = lambda x, y, z=1: (y, x)
    im_shape = swap(*arr.shape)
    im_size = arr.dtype.itemsize * im_channels * im_shape[0]
    im_depth = _cv_depths_inv[str(arr.dtype)]
    im = cv.CreateImageHeader(im_shape, im_depth, im_channels)
    cv.SetData(im, arr.tostring(), im_size)
    return im


DEFAULT_FRAME_ARRAY_DTYPE = 'float32'


def get_frames(file, as_array=True, dtype=None, normal=False):
    '''Return a list of individual frames in a video file.

    If the parameter 'as_array' is True, return NumPy arrays.
    If dtype is specified, return NumPy arrays of that type.
    If the parameter 'normal' is True, normalize the arrays.
    '''

    if dtype is None:
        dtype = DEFAULT_FRAME_ARRAY_DTYPE

    if not _exists(file):
        raise IOError(file)
    cap = cv.CaptureFromFile(file)
    if not cap:
        raise IOError('CaptureFromFile')

    while True:
        img = cv.QueryFrame(cap)
        if not img:
            break
        if as_array:
            img = _cv_to_array(img, dtype=dtype)
            if normal:
                utils.normalize(img)
        yield img


if __name__ == '__main__':
    pass
