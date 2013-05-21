from django.db import models
from cms.models.pluginmodel import CMSPlugin
from django.template.defaultfilters import slugify
from django.utils.translation import ugettext_lazy as _


class SimpleMenu(models.Model):
    """
    Defines a menu for featured links.
    """
    name = models.CharField(_('Menu Name'), max_length=64)
    slug = models.SlugField(
        _('slug'),
        max_length=100,
        unique=True,
        editable=False
    )

    """
    Overide the save method to auto-slug.
    """
    def save(self, *args, **kwargs):
        if not self.slug:
            # Set slug only if new to keep from breaking links.
            self.slug = slugify(self.name)

        super(SimpleMenu, self).save(*args, **kwargs)

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = 'simplemenu'
        verbose_name_plural = 'simplemenus'
        app_label = 'simplemenu'


class Link(models.Model):
    """
    Featured Links
    """
    title = models.CharField(max_length=50)
    url = models.URLField(
        _('url'),
        null=False,
        blank=False
    )
    simplemenu = models.ForeignKey(
        'SimpleMenu',
        verbose_name='simplemenu',
        null=False,
        blank=False
    )
    date_added = models.DateTimeField(
        _('date added'),
        auto_now_add=True
    )
    date_modified = models.DateTimeField(
        _('date modified'),
        auto_now=True
    )

    def __unicode__(self):
        return u"%s | %s" % (self.title, self.url)

    class Meta:
        verbose_name = 'link'
        verbose_name_plural = 'links'
        app_label = 'simplemenu'


class SimpleMenuPlugin(CMSPlugin):
    """
    Plugin for selecting which simplemenu.
    """
    simplemenu = models.ForeignKey('SimpleMenu')

    class Meta:
        app_label = 'simplemenu'
