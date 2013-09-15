""" Captcha.Visual.Distortions

Distortion layers for visual CAPTCHAs
"""
#
# PyCAPTCHA Package
# Copyright (C) 2004 Micah Dowty <micah@navi.cx>
#

from simplecaptcha.visual import Layer
from PIL import Image
import random
import math


class WigglyBlocks(Layer):
    """Randomly select and shift blocks of the image"""

    def __init__(self, block_size=16, sigma=0.01, iterations=300):
        self.block_size = block_size
        self.sigma = sigma
        self.iterations = iterations
        self.seed = random.random()

    def render(self, image):
        r = random.Random(self.seed)
        for i in range(self.iterations):
            # Select a block
            bx = int(r.uniform(0, image.size[0]-self.block_size))
            by = int(r.uniform(0, image.size[1]-self.block_size))
            block = image.crop(
                (bx, by, bx+self.block_size-1, by+self.block_size-1))

            # Figure out how much to move it.
            # The call to floor() is important so we always round toward
            # 0 rather than to -inf. Just int() would bias the block motion.
            mx = int(math.floor(r.normalvariate(0, self.sigma)))
            my = int(math.floor(r.normalvariate(0, self.sigma)))

            # Now actually move the block
            image.paste(block, (bx+mx, by+my))


class WarpBase(Layer):
    """Abstract base class for image warping. Subclasses define a function that
    maps points in the output image to points in the input image.  This warping
    engine runs a grid of points through this transform and uses PIL's mesh
    transform to warp the image.  """

    filtering = Image.BILINEAR
    resolution = 10

    def get_transform(self, image):
        """Return a transformation function, subclasses should override this"""
        return lambda x, y: (x, y)

    def render(self, image):
        r = self.resolution
        x_points = int(image.size[0] / r + 2)
        y_points = int(image.size[1] / r + 2)
        f = self.get_transform(image)

        # Create a list of arrays with transformed points
        x_rows = []
        y_rows = []
        for j in range(y_points):
            x_row = []
            y_row = []
            for i in range(x_points):
                x, y = f(i*r, j*r)

                # Clamp the edges so we don't get black undefined areas
                x = max(0, min(image.size[0]-1, x))
                y = max(0, min(image.size[1]-1, y))

                x_row.append(x)
                y_row.append(y)
            x_rows.append(x_row)
            y_rows.append(y_row)

        # Create the mesh list, with a transformation for
        # each square between points on the grid
        mesh = []
        for j in range(y_points-1):
            for i in range(x_points-1):
                mesh.append((
                    # Destination rectangle
                    (i*r, j*r, (i+1)*r, (j+1)*r),
                    # Source quadrilateral
                    (x_rows[j  ][i  ], y_rows[j  ][i  ],
                     x_rows[j+1][i  ], y_rows[j+1][i  ],
                     x_rows[j+1][i+1], y_rows[j+1][i+1],
                     x_rows[j  ][i+1], y_rows[j  ][i+1]),
                    ))

        return image.transform(image.size, Image.MESH, mesh, self.filtering)


class SineWarp(WarpBase):
    """Warp the image using a random composition of sine waves"""

    def __init__(self,
                 amplitude_range=(3, 6.5),
                 period_range=(0.04, 0.1)
                 ):
        self.amplitude = random.uniform(*amplitude_range)
        self.period = random.uniform(*period_range)
        self.offset = (random.uniform(0, math.pi * 2 / self.period),
                       random.uniform(0, math.pi * 2 / self.period))

    def get_transform(self, image):
        def trans(x, y):
            a = self.amplitude
            p = self.period
            o = self.offset
            return (math.sin( (y+o[0])*p )*a + x,
                    math.sin( (x+o[1])*p )*a + y)
        return trans

