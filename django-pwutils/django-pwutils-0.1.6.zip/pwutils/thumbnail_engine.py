# -*- coding: utf-8 -*-
from sorl.thumbnail.engines.pil_engine import Engine
try:
    from PIL import Image, ImageColor
except ImportError:
    import Image
    import ImageColor


class ExtendTransparentPILEngine(Engine):

    def create(self, image, geometry, options):
        """
        Processing conductor, returns the thumbnail as an image engine instance
        And remove transparent layer to white color
        """
        image = super(Engine, self).create(image, geometry, options)
        if image.mode == 'RGBA':
            background = Image.new('RGB', image.size,
                                   ImageColor.getcolor('white', 'RGBA'))
            background.paste(image, (0, 0), image)
            image = background

        return image


# TODO rename to DoubleGrayPILEngine
class PWPILEngine(ExtendTransparentPILEngine):

    def create(self, image, geometry, options):
        """
        Processing conductor, returns the thumbnail as an image engine instance
        """
        image = super(PWPILEngine, self).create(image, geometry, options)
        image = self.thumb_bw(image, geometry, options)

        return image

    def thumb_bw(self, image, geometry, options):

        thumb_bw = options.get('thumb_bw', False)
        if thumb_bw:
            size = image.size
            if size[1] > size[0]:
                im2 = image.convert('L')
                img1 = Image.new('RGB', (size[0], size[1] * 2))
                img1.paste(im2, (0, 0))
                img1.paste(image, (0, size[1]))
            else:
                im2 = image.convert('L')
                img1 = Image.new('RGB', (size[0] * 2, size[1]))
                img1.paste(im2, (0, 0))
                img1.paste(image, (size[0], 0))
            return img1
        return image
