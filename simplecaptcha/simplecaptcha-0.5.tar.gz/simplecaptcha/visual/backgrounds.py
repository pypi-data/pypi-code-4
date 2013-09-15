""" Captcha.Visual.Backgrounds

Background layers for visual CAPTCHAs

SimpleCaptcha Package
Forked from PyCAPTCHA Copyright (C) 2004 Micah Dowty <micah@navi.cx>
"""
from simplecaptcha.visual import Layer, pictures
import random
from PIL import Image, ImageDraw


class SolidColor(Layer):
    """A solid color background. Very weak on its own, but good to combine with
    other backgrounds.  """

    def __init__(self, color="white"):
        self.color = color

    def render(self, image):
        image.paste(self.color)


class Grid(Layer):
    """A grid of lines, with a given foreground color.  The size is given in
    pixels. The background is transparent, so another layer (like SolidColor)
    should be put behind it.  """

    def __init__(self, size=16, foreground="black"):
        self.size = size
        self.foreground = foreground
        self.offset = (random.uniform(0, self.size),
                       random.uniform(0, self.size))

    def render(self, image):
        draw = ImageDraw.Draw(image)

        r1 = int(image.size[0] / (self.size + 1))
        for i in range(r1):
            draw.line((i*self.size+self.offset[0],
                       0,
                       i*self.size+self.offset[0],
                       image.size[1]),
                      fill=self.foreground)

        r2 = int(image.size[0] / (self.size + 1))
        for i in range(r2):
            draw.line((0,
                       i*self.size+self.offset[1],
                       image.size[0],
                       i*self.size+self.offset[1]),
                      fill=self.foreground)


class TiledImage(Layer):
    """Pick a random image and a random offset, and tile the rendered image
    with it"""

    def __init__(self, image_factory=pictures.abstract):
        self.tile_name = image_factory.pick()
        self.offset = (random.uniform(0, 1),
                       random.uniform(0, 1))

    def render(self, image):
        tile = Image.open(self.tile_name)
        for j in range(-1, int(image.size[1] / tile.size[1]) + 1):
            for i in range(-1, int(image.size[0] / tile.size[0]) + 1):
                dest = (int((self.offset[0] + i) * tile.size[0]),
                        int((self.offset[1] + j) * tile.size[1]))
                image.paste(tile, dest)


class CroppedImage(Layer):
    """Pick a random image, cropped randomly. Source images should be larger
    than the CAPTCHA."""

    def __init__(self, image_factory=pictures.nature):
        self.image_name = image_factory.pick()
        self.align = (random.uniform(0, 1),
                      random.uniform(0, 1))

    def render(self, image):
        i = Image.open(self.image_name)
        image.paste(i, (int(self.align[0] * (image.size[0] - i.size[0])),
                        int(self.align[1] * (image.size[1] - i.size[1]))))


class RandomDots(Layer):
    """Draw random colored dots"""
    def __init__(self, colors=("white", "black"), dot_size=4, num_dots=400):
        self.colors = colors
        self.dot_size = dot_size
        self.num_dots = num_dots
        self.seed = random.random()

    def render(self, image):
        r = random.Random(self.seed)
        for i in range(self.num_dots):
            bx = int(r.uniform(0, image.size[0]-self.dot_size))
            by = int(r.uniform(0, image.size[1]-self.dot_size))
            image.paste(r.choice(self.colors), (bx, by,
                                                bx+self.dot_size-1,
                                                by+self.dot_size-1))
