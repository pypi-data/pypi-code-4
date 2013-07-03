from cms.models.pluginmodel import CMSPlugin
from django.utils.translation import ugettext_lazy as _
from django.db import models

PLUGIN_TEMPLATES = (
    ('cms_plugins/fb_album.html', 'Carousel effect'),
    ('cms_plugins/fb_album_lightbox.html', 'Light effect'),
)


class Fb(CMSPlugin):
    album_url = models.CharField(_('Album Url'), max_length=125)
    access_token = models.CharField('Access token', max_length=500)
    album_name = models.CharField('Album Name', max_length=75)
    template = models.CharField('Template', max_length=255,
        choices = PLUGIN_TEMPLATES)
