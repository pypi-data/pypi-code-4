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

Box = namedtuple("Box", ['wscale', 'hscale', 'left', 'top', 'right', 'bottom'])
Size = namedtuple("Size", ['width', 'height'])
_Box = Box
_Size = Size


def box(width, height):
    return new_box(width, height, 0, 0, width, height)

def new_box(width, height, left, top, right, bottom):
    return Box(
        wscale=Fraction(1),
        hscale=Fraction(1),
        left=left,
        top=top,
        right=right,
        bottom=bottom
    )


def resize(box, width, height):
    """
    >>> from testfixtures import compare
    >>> _ = compare(
    ...     resize(
    ...        Box(1.0, 1.0, 0, 0, 100, 100),
    ...        50, 50
    ...     ),
    ...  Box(wscale=0.5, hscale=0.5, left=0.0, top=0.0, 
    ...      right=100.0, bottom=100.0)
    ... )
    """
    cw = box.right - box.left
    ch = box.bottom - box.top
    ws = Fraction(width,  cw)
    hs = Fraction(height, ch)

    return Box(
        ws,
        hs,
        box.left,
        box.top,
        box.right,
        box.bottom
    )

def crop(box, left, top, right, bottom):
    """
    >>> crop(
    ...     Box(0.5, 0.5, 0, 0, 100, 100),
    ...     0, 0, 25, 25
    ... )
    Box(wscale=0.5, hscale=0.5, left=0.0, top=0.0, right=50.0, bottom=50.0)

    """
    (l,t,r,b) = scale_crop(left, top, right, bottom,box.wscale, box.hscale)
    return Box(
        box.wscale,
        box.hscale,
        l,t,r,b
    )


def scale_crop(l,t,r,b, ws, hs):
    return (
        l / ws,
        t / hs,
        r / ws,
        b / hs
    )
        
        

def make_transformer(box, resize_cb, crop_cb):
    def inner(img0):
        ws = box.wscale
        hs = box.hscale
        cw = box.right - box.left
        ch = box.bottom - box.top
        width = cw * ws
        height = ch * hs
        
        img1 = crop_cb(
            img0,
            box.left,
            box.top,
            box.right,
            box.bottom
        )
        img2 = resize_cb(img1, width, height)
        return img2

    return inner


def size(box):
    """Return the actual size of the box"""
    ws = box.wscale
    hs = box.hscale
    cw = box.right - box.left
    ch = box.bottom - box.top
    width = cw * ws
    height = ch * hs
    return _Size(width, height)
