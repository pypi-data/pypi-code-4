"""
This module allows crop and resize operations to be applied in a chain
and the resulting in a final resize and crop operation calculated from that chain.

This is to efficiantly resize an image without repeated resize operations which degrade quality.
"""
import sys
from collections import namedtuple

# If we're in 2.6, use the backported 2.7 fractions module
if sys.version_info < (2,7):
    from fractions27 import Fraction
else:
# otherwise use the native one
    from fractions import Fraction

_Box = namedtuple("Box", ['width', 'height', 'left', 'top', 'right', 'bottom'])
_Size = namedtuple("Size", ['width', 'height'])

def box(width, height):
    return new_box(width, height, 0, 0, width, height)


def new_box(width, height, left, top, right, bottom):
    return _Box(
        width,
        height,
        left,
        top,
        right,
        bottom,
    )


def resize(box, width, height):
    """
    >>> resize(
    ...    Box(100, 100, 0, 0, 50, 50), # resulting image is 50x50
    ...    50, 50
    ... )
    Box(width=100.0, height=100.0, left=0.0, top=0.0, right=50.0, bottom=50.0)

    Takes a 0,0,100,100 crop of a 200x200 image.
    which results in a 100x100 and resizes it to 50x50

    This should scale everything by 1/2

    >>> resize(
    ...    Box(200, 200, 0, 0, 100, 100),
    ...    50, 50
    ... )
    Box(width=100.0, height=100.0, left=0.0, top=0.0, right=50.0, bottom=50.0)

    >>> resize(
    ...    Box(200, 200, 0, 0, 100, 100),
    ...    200, 200
    ... )
    Box(width=400.0, height=400.0, left=0.0, top=0.0, right=200.0, bottom=200.0)
    """
    new_width, left, right = scale_dimension(
        width,
        box.width,
        box.left,
        box.right
    )

    new_height, top, bottom = scale_dimension(
        height,
        box.height,
        box.top,
        box.bottom
    )

    return new_box(
        new_width, new_height,
        left, top, right, bottom
    )


def crop(box, left, top, right, bottom):
    """
    >>> crop(
    ...     Box(320, 200, 10, 20, 30, 40),
    ...     0, 0, 15, 25
    ... )
    Box(width=320, height=200, left=10, top=20, right=25, bottom=45)
    """
    return new_box(
        box.width,
        box.height,
        box.left + left,
        box.top + top,
        box.left + right,
        box.top + bottom,
   )


def make_transformer(box, resize_cb, crop_cb):
    def inner(img0):
        img1 = resize_cb(img0, box.width, box.height)
        return crop_cb(
            img1,
            box.left,
            box.top,
            box.right,
            box.bottom
        )
    return inner


def size(box):
    """Return the actual size of the box"""
    width = box.right - box.left
    height = box.bottom - box.top
    return _Size(width, height)


###-------------------------------------------------------------------
### Internal
###-------------------------------------------------------------------
def scale_dimension(req_size, orig_size, offset1, offset2):
    assert orig_size > 0
    assert req_size > 0
    assert offset1 != offset2
    assert req_size > 0

    crop_size = offset2 - offset1
    # Get the amount we need to scale everything to
    scale = Fraction(req_size, crop_size)

    # do the scaling to get the requested size out of the resize and crop
    new_size = orig_size * scale
    new_offset1 = offset1 * scale
    new_offset2 = offset2 * scale
    return new_size, new_offset1, new_offset2
