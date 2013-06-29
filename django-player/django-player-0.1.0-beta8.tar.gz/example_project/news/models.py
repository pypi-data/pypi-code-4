# Copyright (c) 2010 by Manuel Saelices
#
# This file is part of django-playerlayer.
#
# django-playerlayer is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# django-playerlayer is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with django-playerlayer.  If not, see <http://www.gnu.org/licenses/>.

from django.db import models
from django.utils.translation import ugettext_lazy as _


class NewsCategory(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=100)

    class Meta:
        verbose_name = _('news category')
        verbose_name_plural = _('news categories')

    def __unicode__(self):
        return self.title


class NewsItem(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=100)

    publish_date = models.DateTimeField(db_index=True)
    category = models.ForeignKey(NewsCategory,
                                 verbose_name=_('category'))
    body = models.TextField(_('body'))

    class Meta:
        ordering = ('-publish_date', '-id')
        verbose_name = _('news item')
        verbose_name_plural = _('news')

    def __unicode__(self):
        return self.title

    @models.permalink
    def get_absolute_url(self):
        return ('news_detail', (), {'news_slug': self.slug})
