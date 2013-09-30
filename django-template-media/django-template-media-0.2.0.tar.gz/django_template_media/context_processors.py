from __future__ import absolute_import, unicode_literals
from .templatetags.media_tags import MEDIA_KEY, MediaContainer


def template_media(request):
    return {
        MEDIA_KEY: MediaContainer()
    }
