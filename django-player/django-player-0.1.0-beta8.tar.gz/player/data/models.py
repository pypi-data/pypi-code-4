# Copyright (c) 2010 by Yaco Sistemas
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

from datetime import datetime

from django.db import models
from django.db.models.signals import post_save
from django.utils.translation import ugettext
from django.utils.translation import ugettext_lazy as _

from configfield.dbfields import JSONField
from player.logicaldelete import models as logicaldelete_models
from player.base.dbfields import AutoSlugField
from player.crawler import get_backend
from player.crawler.models import CrawlerCollection
from player.data.exceptions import DateConversionError
from player.data.managers import ItemManager, CollectionFieldManager, CollectionManager
from player.data.structures import ItemData


STATUS_LIST = (
    ('draft', _('Draft')),
    ('published', _('Published')),
)

FIELD_TYPES = (
    ('int', _('Integer')),
    ('date', _('Date')),
    ('text', _('Text')),
    ('html', _('HTML text')),
    ('url', _('URL')),
)


class CollectionGroup(models.Model):
    """ Represent a entire web site to parse """
    name = models.CharField(_('name'), max_length=200, unique=True)
    slug = AutoSlugField(autofromfield='name')

    class Meta:
        verbose_name = _('CollectionGroup')

    def __unicode__(self):
        return self.name

    @models.permalink
    def get_absolute_url(self):
        return ('player.data.views.collectiongroup_view', [self.slug])


class Collection(models.Model):
    """ Represent a content type (news, events, etc) """
    name = models.CharField(_('Name'), max_length=200, unique=True)
    slug = models.SlugField()
    collectiongroup = models.ForeignKey(CollectionGroup, verbose_name=_('Group'),
                                        null=True, blank=True)
    crawler_collection = models.ForeignKey(CrawlerCollection, null=True, blank=True)
    status = models.CharField(max_length=100, choices=STATUS_LIST,
                              default='draft')
    repr_field = models.OneToOneField(
        'CollectionField', verbose_name=_('Field representing item'),
        related_name='repr_collection', null=True, blank=True,
        help_text=_('Field in collection schema that will represent to content'),
    )
    crawling_checked = models.BooleanField(_(u'Crawling checked'), default=False)
    objects = CollectionManager()
    last_crawling_time = models.DateTimeField(_('Last crawling time'),
                                              null=True, blank=True)

    class Meta:
        verbose_name = _('Collection')

    def __unicode__(self):
        return self.name

    @models.permalink
    def get_absolute_url(self):
        return ('player.data.views.collection_view', [self.collectiongroup.slug, self.slug])

    def _stripped_name(self):
        """ used to remove all '-' in slug for configuration file """
        return self.slug.replace('-', '')
    stripped_name = property(_stripped_name)

    def _collection_link(self):
        return get_backend(self.crawler_collection.backend).get_collection_link(self.crawler_collection)
    collection_link = property(_collection_link)

    def is_well_defined(self):
        mapped = True
        fields = CollectionField.objects.filter(collection=self)
        for field in fields:
            if field.mapped_field == None:
                mapped = False

        return self.repr_field and mapped

    def first_crawl_done(self):
        return (self.last_crawling_time != None)

    def is_published(self):
        return self.status == 'published'

    def is_publishable(self):
        """
        Returns if collection can be publishable as collection
        because it complains all the requirements.
        """
        return self.crawling_checked and \
               self.is_well_defined() and self.first_crawl_done()

    def is_mapped(self):
        """ Returns if collection has mapped any field to any crawling collection """
        return self.crawler_collection is not None and self.fields.is_mapped().exists()


class CollectionField(models.Model):
    name = models.CharField(_('Name'), max_length=200)
    slug = models.SlugField()
    field_type = models.CharField(_('Field type'), max_length=20,
                                  default='text', choices=FIELD_TYPES)
    collection = models.ForeignKey(Collection, related_name='fields')
    is_matchup = models.BooleanField(_('Is matchup'), default=False)
    custom_format = models.CharField(_('Custom format'), max_length=200,
                                    null=True, blank=True)
    mapped_field = models.CharField(_('Mapped field'), max_length=200,
                                    null=True, blank=True)

    objects = CollectionFieldManager()

    def __unicode__(self):
        return self.name

    def delete(self):
        collection = self.collection
        collection_modified = False
        if collection.repr_field == self:
            collection.repr_field = None
            collection.save()
        super(CollectionField, self).delete()


class Item(logicaldelete_models.Model):
    """ Represent a item (news item, event, etc.) """
    uid = models.CharField(max_length=200)
    content = JSONField(editable=False)
    collection = models.ForeignKey(Collection)
    title = models.CharField(max_length=300, default='')
    is_valid = models.BooleanField(_('Is valid'), default=True)

    objects = ItemManager()

    class Meta:
        verbose_name = _('Item')
        unique_together = (('uid', 'collection', 'is_valid', 'is_deleted'), )

    def __init__(self, *args, **kwargs):
        super(Item, self).__init__(*args, **kwargs)
        self.data = ItemData(self)

    def __unicode__(self):
        collection = self.collection
        repr_field = collection.repr_field
        if repr_field and self.content is not None and repr_field.slug in self.content:
            return self.get_value_from_field(repr_field)
        return self.get_uid()

    @models.permalink
    def get_manage_url(self):
        return ('player.data.views.item_view', [self.collection.collectiongroup.slug, self.id])

    def get_uid(self):
        if not self.id:
            return 'not-saved-%s' % self.uid
        return '%d-%s' % (self.id, self.uid)

    def get_title(self):
        return self.collection.repr_field and self.get_value_from_field(self.collection.repr_field) or self.uid

    def get_value_from_field(self, field):
        return self.get_value(field.slug)

    def get_value(self, field_slug):
        """ get item value using mapped schema """
        # TODO: do type conversion if needed
        value = self.content[field_slug]
        if value is None:
            return None  # avoid next SQL sentences
        field = self.collection.fields.get(slug=field_slug)
        if field.field_type == 'date':
            date_format = field.custom_format or '%d/%m/%Y'
            try:
                value = datetime.strptime(value, date_format).isoformat()
            except ValueError:
                raise DateConversionError(
                    ugettext(u'Date conversion error: "%(value)s" value is not in format "%(format)s"') %
                    {'value': value, 'format': date_format},
                )
        return value

    def update_content(self, new_content):
        """ Update content extracted from player.crawler """
        self.content = new_content
        self._update_parsed_data()

    def update_title(self):
        if self.collection.repr_field and self.collection.repr_field.slug in self.content:
            max_length = self._meta.get_field_by_name('title')[0].max_length
            slug = self.content[self.collection.repr_field.slug]
            self.title = slug and slug[:max_length] or u'No title'
        else:
            self.title = ''

    def save(self, *args, **kwargs):
        if not self.id and not self.content:  # new item
            self.content = {}
        self.update_title()
        super(Item, self).save(*args, **kwargs)

    def has_changed(self, new_content):
        return self.content != new_content


def handle_item_save(sender, instance, created, **kwargs):
    if created:
        Item.objects.only_deleted().filter(uid=instance.uid, collection=instance.collection).delete()

post_save.connect(handle_item_save, sender=Item)
