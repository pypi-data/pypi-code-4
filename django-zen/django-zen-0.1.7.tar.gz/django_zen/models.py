from django.utils.translation import ugettext as _
from django.db import models
from redactor.fields import RedactorField
from mptt.models import MPTTModel, TreeForeignKey
from django.utils.encoding import iri_to_uri
from django.core.urlresolvers import get_script_prefix
from django.utils.functional import lazy
from django.conf import settings
import os


class Menu(MPTTModel):
    name = models.CharField(_('Name'), max_length=255)
    url = models.CharField(_('URL'), max_length=255, blank=True, null=True)
    menu_id = models.SlugField(_('Menu ID'), blank=True, null=True)
    parent = TreeForeignKey('self', null=True, blank=True, related_name='children')
    published = models.BooleanField(_('Published'), default=True)

    class Meta:
        verbose_name = _('Menu')
        verbose_name_plural = _('Menus')

    def __unicode__(self):
        return self.name


def pages_templates():
    templates_path = os.path.join(settings.TEMPLATE_DIRS[0], 'pages')
    pages_templates = os.listdir(templates_path)
    pages_templates = tuple([(pt, pt) for pt in pages_templates])
    return pages_templates


class Page(models.Model):
    url = models.CharField(_('URL'), max_length=255)
    title = models.CharField(_('Page title'), max_length=255, blank=True, null=True)
    published = models.BooleanField(_('Published'), default=True)
    content = RedactorField(_('Content'), blank=True)
    template = models.CharField(_('Template name'), max_length=70,
        choices=lazy(pages_templates, tuple)(), blank=True, null=True)
    menu = models.ForeignKey(Menu, blank=True, null=True)

    def get_absolute_url(self):
        return iri_to_uri(get_script_prefix().rstrip('/') + self.url)

    class Meta:
        verbose_name = _('Page')
        verbose_name_plural = _('Pages')

    def __unicode__(self):
        return self.url
