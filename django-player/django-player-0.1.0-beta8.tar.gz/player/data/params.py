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

from configfield import params
from player.data.models import Collection


def get_collections_choices():
    return [(c.slug, c.name) for c in Collection.objects.all()]


class CollectionParam(params.Param):

    def __init__(self, *args, **kwargs):
        super(CollectionParam, self).__init__(*args, **kwargs)
        if 'choices' not in kwargs:
            self.choices = get_collections_choices

    def is_valid(self, value):
        return super(CollectionParam, self).is_valid(value) and \
               Collection.objects.filter(slug=value)

    def get_value(self):
        value = super(CollectionParam, self).get_value()
        try:
            return Collection.objects.get(slug=value)
        except Collection.DoesNotExist:
            return None
