### -*- coding: utf-8 -*- ####################################################
##############################################################################
#
# Copyright (c) 2008 Thierry Florac <tflorac AT ulthar.net>
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################


# import standard packages
from cStringIO import StringIO
from PIL import Image, ImageFilter, ImageEnhance

# import Zope3 interfaces
from zope.app.file.interfaces import IImage

# import local interfaces
from ztfy.file.interfaces import IThumbnailer, IThumbnailGeometry, IWatermarker, DEFAULT_DISPLAYS

# import Zope3 packages
from zope.interface import implements

# import local packages


class PILThumbnailer(object):
    """PIL thumbnailer utility"""

    implements(IThumbnailer)

    order = 50

    def createThumbnail(self, image, size, format=None):
        # init image
        if IImage.providedBy(image):
            image = image.data
        image = Image.open(StringIO(image))
        # check format
        if not format:
            format = image.format
        format = format.upper()
        if format not in ('GIF', 'JPEG', 'PNG'):
            format = 'JPEG'
        # check mode
        if image.mode == 'P':
            image = image.convert('RGBA')
        # generate thumbnail
        new = StringIO()
        image.resize(size, Image.ANTIALIAS).filter(ImageFilter.SHARPEN).save(new, format)
        return new.getvalue(), format.lower()

    def createSquareThumbnail(self, image, size, source=None, format=None):
        # init image
        if IImage.providedBy(image):
            image = image.data
        image = Image.open(StringIO(image))
        # check format
        if not format:
            format = image.format
        format = format.upper()
        if format not in ('GIF', 'JPEG', 'PNG'):
            format = 'JPEG'
        # check mode
        if image.mode == 'P':
            image = image.convert('RGBA')
        # compute thumbnail size
        img_width, img_height = image.size
        thu_width, thu_height = size, size
        ratio = max(img_width * 1.0 / thu_width, img_height * 1.0 / thu_height)
        if source:
            x, y, w, h = source
        else:
            geometry = IThumbnailGeometry(image)
            (x, y), (w, h) = geometry.position, geometry.size
        box = (int(x * ratio), int(y * ratio), int((x + w) * ratio), int((y + h) * ratio))
        # generate thumbnail
        new = StringIO()
        image.crop(box).resize((DEFAULT_DISPLAYS['cthumb'], DEFAULT_DISPLAYS['cthumb']), Image.ANTIALIAS).filter(ImageFilter.SHARPEN).save(new, format)
        return new.getvalue(), format.lower()


class PILWatermarker(object):
    """PIL watermarker utility"""

    implements(IWatermarker)

    order = 50

    def _reduce_opacity(self, image, opacity):
        """Returns an image with reduced opacity."""
        assert opacity >= 0 and opacity <= 1
        if image.mode != 'RGBA':
            image = image.convert('RGBA')
        else:
            image = image.copy()
        alpha = image.split()[3]
        alpha = ImageEnhance.Brightness(alpha).enhance(opacity)
        image.putalpha(alpha)
        return image

    def addWatermark(self, image, mark, position='scale', opacity=1, format=None):
        """Adds a watermark to an image and return a new image"""
        # init image
        if IImage.providedBy(image):
            image = image.data
        image = Image.open(StringIO(image))
        # check format
        if not format:
            format = image.format
        format = format.upper()
        if format not in ('GIF', 'JPEG', 'PNG'):
            format = 'JPEG'
        # check RGBA mode
        if image.mode != 'RGBA':
            image = image.convert('RGBA')
        # init watermark
        if IImage.providedBy(mark):
            mark = mark.data
        mark = Image.open(StringIO(mark))
        if opacity < 1:
            mark = self._reduce_opacity(mark, opacity)
        # create a transparent layer the size of the image and draw the
        # watermark in that layer.
        layer = Image.new('RGBA', image.size, (0, 0, 0, 0))
        if position == 'tile':
            for y in range(0, image.size[1], mark.size[1]):
                for x in range(0, image.size[0], mark.size[0]):
                    layer.paste(mark, (x, y))
        elif position == 'scale':
            # scale, but preserve the aspect ratio
            ratio = min(float(image.size[0]) / mark.size[0], float(image.size[1]) / mark.size[1])
            w = int(mark.size[0] * ratio)
            h = int(mark.size[1] * ratio)
            mark = mark.resize((w, h))
            layer.paste(mark, ((image.size[0] - w) / 2, (image.size[1] - h) / 2))
        else:
            layer.paste(mark, position)
        # composite the watermark with the layer
        new = StringIO()
        Image.composite(layer, image, layer).save(new, format)
        return new.getvalue(), format.lower()
