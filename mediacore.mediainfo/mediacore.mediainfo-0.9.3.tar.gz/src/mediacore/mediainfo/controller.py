# -*- coding: UTF-8 -*-

from mediacore.lib.base import BaseController
from mediacore.lib.decorators import expose
from mediacore.lib.thumbnails import thumb_url
from mediacore.model import fetch_row, Media

class Controller(BaseController):

    @expose('json')
    def media_unique_id(self, slug=None, **kwargs):
        if slug:
            media = fetch_row(Media, slug=slug)
            file_ = media.files[0]
            if file_:
                return {
                        'unique_id': file_.unique_id,
                        'file_id': str(file_.id),
                        'image_url': thumb_url(media, 'l', qualified=True),
                        }

