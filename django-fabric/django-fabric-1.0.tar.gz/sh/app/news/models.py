# -*- coding: utf-8 -*-
from django.db import models
from django.utils.translation import ugettext_lazy as _
from ckeditor import fields
from sh.core.models import BaseModel

class NewsItem (BaseModel):
    title = models.CharField(max_length=250, verbose_name=_('title'))
    slug = models.SlugField(verbose_name=_('slug'), help_text=_('This is the text that will follow starthjelpa.no/nyheter/ in the URL'))
    pub_date = models.DateTimeField(verbose_name=_('publish date'))
    sticky = models.BooleanField(help_text=_('Check this if you want the news to appear on top of the news page'))
    content = fields.RichTextField(verbose_name=_('content'))

    class Meta:
        ordering = ('sticky', '-pub_date')

    def __unicode__(self):
        return self.title

