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

from django.core.exceptions import ImproperlyConfigured


class ItemData(dict):
    """ item has a raw JSON of data extracted from backend. ItemData
    is a dictionary with cooked data (i.e. dates will be datetime values"""

    def __init__(self, item):
        self.item = item
        self.data = dict()
        self.collection = item.collection

    def __getitem__(self, key):
        if key not in self and key in self.item.content:
            # populate dict lazily
            self.data[key] = self.item.get_value(key)
        try:
            return self.data[key]
        except KeyError:
            fields_slugs = ['"%s"' % f.slug for f in self.collection.fields.all()]
            raise ImproperlyConfigured(
                'You want to get the "%s" field of "%s" item, but the collection only has defined these fields: %s' %
                (key, self.item, ', '.join(fields_slugs))
            )

    def __unicode__(self):
        # TODO: optimize SQL sentences launched in this method
        if self.item:
            for field_slug, raw_value in self.item.content.items():
                self.data[str(field_slug)] = self.item.get_value(field_slug)
        return unicode(self.data)
