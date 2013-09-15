""" Captcha.Visual.Pictures

Random collections of images

SimpleCaptcha Package
Forked from PyCAPTCHA Copyright (C) 2004 Micah Dowty <micah@navi.cx>
"""

from simplecaptcha import file


class ImageFactory(file.RandomFileFactory):
    """A factory that generates random images from a list"""
    extensions = [".png", ".jpeg"]
    base_path = "pictures"


abstract = ImageFactory("abstract")
nature = ImageFactory("nature")
