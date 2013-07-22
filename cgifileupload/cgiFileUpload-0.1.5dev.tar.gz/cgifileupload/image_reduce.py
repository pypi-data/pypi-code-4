
import os, sys
from PIL import Image
import logging


log = logging.getLogger(__name__)


def scale_image(image_file, max_x=1040, max_y=702):
    '''
    If the image is too big (physically) for the screen we need to reduce it.
    Rather than having an 'original' and a scaled down (but still fullsize)
    version, we effective resize it in place if the dimensions are too great.
    '''

    im = Image.open(image_file)

    x, y = im.size
    log.debug("x: %d, y: %d", x, y)

    ratio = min(float(max_x)/x, float(max_y)/y)

    if ratio < 1:
        log.debug("resize required")

        new_size = int(x * ratio), int(y * ratio)

        im.resize(new_size).save(image_file)

        log.debug("resized to x: %d, y: %d", new_size[0], new_size[1])


    else:
        log.debug("no resize required")


