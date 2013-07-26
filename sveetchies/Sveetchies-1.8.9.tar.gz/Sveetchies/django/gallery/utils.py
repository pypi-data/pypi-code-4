# -*- coding: utf-8 -*-
"""
Utils
"""
import os

from django.conf import settings

from Sveetchies.imaging.picture import PictureLayout, PictureAdapt
from Sveetchies.logger.new import DummyInterface
from Sveetchies.django.filefield import content_file_name
from Sveetchies.django.gallery import IMAGE_FORMATS_CHOICES, IMAGE_FORMAT_DEFAULT

def adapt_source(source, uploadpath, layoutstring, logger=None):
    """
    Méhode pour crée une version redimensionnée d'une image
    """
    destination_rel = content_file_name(uploadpath, None, os.path.basename(source), new_extension=IMAGE_FORMATS_CHOICES[IMAGE_FORMAT_DEFAULT])
    destination_path = os.path.join(settings.MEDIA_ROOT, destination_rel)
    if not logger:
        logger = DummyInterface()
    layout = PictureLayout.from_layout(layoutstring)
    picture = PictureAdapt(logger, layout, source, destination_path, debug=False)
    picture.resize(target_format=IMAGE_FORMAT_DEFAULT)
    
    return destination_rel
