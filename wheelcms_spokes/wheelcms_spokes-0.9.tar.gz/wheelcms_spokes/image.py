from django.db import models
from wheelcms_axle.content import type_registry, ImageContent
from wheelcms_axle.templates import template_registry
from wheelcms_axle.spoke import FileSpoke


class Image(ImageContent):
    """ Holds an image.  """
    ## cannot be named image - that's used for the content base relation
    storage = models.ImageField(upload_to="images", blank=False)

class ImageType(FileSpoke):
    model = Image

    title = "An image"
    children = ()

    default_language = 'any'  # images are usually not language specific

    type_icon = icon = "image.png"

    def detail_template(self):
        """ A small detail template, used in browse modal """
        return "wheelcms_spokes/image_detail.html"

template_registry.register(ImageType, "wheelcms_spokes/image_view.html", "Basic Image view", default=True)
type_registry.register(ImageType)
