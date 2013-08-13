# -*- coding: utf-8 -*-
from datetime import datetime
from django.conf import settings
from django.core.cache import cache
from django.utils.translation import ugettext_lazy as _
from django.db import models
from sh.core.models import BaseModel
from sh.core.util import slugify
from ckeditor import fields

class Category(BaseModel):
    title = models.CharField(max_length=25, verbose_name=_('title'))
    slug = models.CharField(max_length=30, editable=False)

    def __unicode__(self):
        return self.title

    def save(self, *args, **kwargs):
        self.slug = slugify(self.title)
        super(Category, self).save(*args, **kwargs)


class PageRevision(BaseModel):
    revision_id = models.PositiveIntegerField(editable=False)
    page = models.ForeignKey('Page', editable=False, related_name='revisions')
    content = models.TextField(editable=False)
    date = models.DateTimeField(auto_now_add=True, editable=False)

    def __unicode__(self):
        return '%s revision %s' % (self.page.title, self.id)

    def save(self, *args, **kwargs):
        last = PageRevision.objects.filter(page=self.page)
        if last.count() > 0:
            self.revision_id = last[0].revision_id + 1
        else:
            self.revision_id = 1
        super(PageRevision, self).save(*args, **kwargs)

    @classmethod
    def create_revision(cls, page):
        r = PageRevision(page=page, content=page.content, date=datetime.now())
        r.save()


class Page(BaseModel):
    title = models.CharField(max_length=250, verbose_name=_('title'))
    menu_title = models.CharField(max_length=250, verbose_name=_('menu title'), help_text=_('This is the title that will be displayed in the menu'))
    slug = models.SlugField(verbose_name=_('slug'), help_text=_('This is the text that will follow starthjelpa.no in the URL'))
    weight = models.IntegerField(max_length=2, verbose_name=_('weight'), help_text=_('Lower weight will move the menu item to the front of the menu'))
    category = models.ForeignKey(Category, related_name='pages', null=True, blank=True, verbose_name=_('category'))
    content = fields.RichTextField(verbose_name=_('content'))

    class Meta:
        ordering = ('title',)

    def __unicode__(self):
        return self.title

    def save(self, *args, **kwargs):
        self.slug = slugify(self.menu_title)
        super(Page, self).save(*args, **kwargs)

        PageRevision.create_revision(self)

        key = "page%s" % self.slug
        cache.set(key, self)
        cache.delete('mainnav')

        if self.pk == settings.FRONTPAGE_ID:
            cache.set('frontpage', self)

    def delete(self, *args, **kwargs):
        """
        Must delete all page-revisions, since the foreignkey is not null.
        """
        for page_rev in self.revisions.all():
            page_rev.delete()
        cache.delete('page%s' % self.slug)
        cache.delete('mainnav')
        super(Page, self).delete(*args, **kwargs)




