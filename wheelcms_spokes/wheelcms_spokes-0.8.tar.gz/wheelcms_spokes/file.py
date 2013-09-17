from django.db import models

from wheelcms_axle.models import type_registry
from wheelcms_axle.templates import template_registry
from wheelcms_axle.content import FileContent
from wheelcms_axle.spoke import FileSpoke

class File(FileContent):
    """ Holds a file """
    ## cannot be named file - that's used for the content base relation
    storage = models.FileField(upload_to="files", blank=False)


## hide filename from form - extract it from uploaded file.
##
## provide list of mimetypes for mimetype, provide detection option

class FileType(FileSpoke):
    model = File

    title = "A file"
    children = ()

    type_icon = icon = "file.png"

    def detail_template(self):
        """ A small detail template, used in browse modal """
        return "wheelcms_spokes/file_detail.html"


template_registry.register(FileType, "wheelcms_spokes/file_view.html", "Basic File view", default=True)
type_registry.register(FileType)
