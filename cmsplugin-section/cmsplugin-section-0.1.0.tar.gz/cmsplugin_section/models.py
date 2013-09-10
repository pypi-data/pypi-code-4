from django.db import models
from cms.models import CMSPlugin
try:
    from djangocms_text_ckeditor.fields import HTMLField
    _USE_HTML = True
except ImportError:
    _USE_HTML = False
import utils


class Section(CMSPlugin):
    title = models.CharField(max_length=200, blank=True)
    if _USE_HTML:
        content = HTMLField(blank=True)
    else:
        content = models.TextField(blank=True)

    render_template = models.CharField(max_length=100, blank=True,
        choices=utils.CMSPLUGIN_SECTION_TEMPLATES)

    options_storage = models.TextField(blank=True,
        verbose_name=u'Options')
    enabled = models.BooleanField(default=True)

    class Meta:
        db_table = 'cmsplugin_sections'

    def __unicode__(self):
        template = self.get_render_template_display()
        return u'{}{}: {}'.format(
            (u'' if self.enabled else u'[-] '), template, self.title)

    def options(self):
        return utils.get_options(self.options_storage)
