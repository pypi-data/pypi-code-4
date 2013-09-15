""" Captcha.Visual

This package contains functionality specific to visual CAPTCHA tests.

SimpleCaptcha Package
Forked from PyCAPTCHA Copyright (C) 2004 Micah Dowty <micah@navi.cx>
"""

import simplecaptcha
from PIL import Image


class ImageCaptcha(simplecaptcha.BaseCaptcha):
    """Base class for image-based CAPTCHA tests.  The render() function
    generates the CAPTCHA image at the given size by combining Layer instances
    from self.layers, which should be created by the subclass-defined
    getLayers().  """

    default_size = (256, 96)

    def __init__(self, *args, **kwargs):
        simplecaptcha.BaseCaptcha.__init__(self)
        self._layers = self.get_layers(*args, **kwargs)
        self._image = None

    def get_image(self):
        """Get a PIL image representing this CAPTCHA test, creating it if
        necessary"""
        if self._image is None:
            self._image = self.render()
        return self._image

    def get_layers(self):
        """Subclasses must override this to return a list of Layer instances to
        render.  Lists within the list of layers are recursively rendered.  """
        return []

    def render(self, size=None):
        """Render this CAPTCHA, returning a PIL image"""
        if size is None:
            size = self.default_size
        img = Image.new("RGB", size)
        return self._render_list(self._layers, img)

    def _render_list(self, l, img):
        for i in l:
            if type(i) == tuple or type(i) == list:
                img = self._render_list(i, img)
            else:
                img = i.render(img) or img
        return img


class Layer(object):
    """A renderable object representing part of a CAPTCHA.  The render()
    function should return approximately the same result, regardless of the
    image size. This means any randomization must occur in the constructor.

    If the render() function returns something non-None, it is taken as an
    image to replace the current image with. This can be used to implement
    transformations that result in a separate image without having to copy the
    results back to the first.  """

    def render(self, img):
        pass
