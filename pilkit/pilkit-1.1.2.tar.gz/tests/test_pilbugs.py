"""
Test workarounds for PIL Issues

"""

from pilkit.lib import Image, ImageDraw
from pilkit.processors import (Resize, ResizeToFill, ResizeToFit, SmartCrop,
                               SmartResize)
from nose.tools import eq_, assert_true
from .utils import create_image
from pilkit.lib import StringIO
from pilkit.utils import save_image


def test_large_exif():
    # https://github.com/python-imaging/Pillow/issues/148
    im = create_image()
    save_image(im, StringIO(), 'JPEG', options={'quality': 90, exif=b'1'*65532}, autoconvert=False)
