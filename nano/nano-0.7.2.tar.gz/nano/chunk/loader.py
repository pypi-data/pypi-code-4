"""
Wrapper for loading templates from the filesystem.
"""

from django.conf import settings
from django.template.base import TemplateDoesNotExist
from django.template.loader import BaseLoader
from django.utils._os import safe_join

from django.db import models

Chunk = models.get_model('chunk', 'Chunk')

class Loader(BaseLoader):
    is_usable = True

    def load_template_source(self, template_name, template_dirs=None):
        chunk_model_name = Chunk.__name__
        try:
            chunk = Chunk.objects.get(slug=template_name)
            return (chunk.content, "chunk:%s:%s" % (chunk_model_name, template_name))
        except Chunk.DoesNotExist:
            error_msg = "Couldn't find a %s-chunk with the name %s" % (chunk_model_name, template_name)
            raise TemplateDoesNotExist(error_msg)

_loader = Loader()
