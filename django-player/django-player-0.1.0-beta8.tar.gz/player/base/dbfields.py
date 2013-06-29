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

# code taken from Merengue CMS

from django.db import models
from django.template import defaultfilters


def get_ordered_parents(model):
    """
    Returns a list of all the ancestor of this model as a list.
    """
    result = []
    for parent in model._meta.parents:
        result.append(parent)
        result.extend(get_ordered_parents(parent))
    return result


class AutoSlugField(models.SlugField):

    def __init__(self, autofromfield, *args, **kwargs):
        self.force_on_edit = kwargs.pop('force_on_edit', False)
        self.unique_on_parent_model = kwargs.pop('unique_on_parent_model', False)
        super(AutoSlugField, self).__init__(*args, **kwargs)
        self.autofromfield = autofromfield
        self.editable = kwargs.get('editable', False)

    def sluggify(self, name, objects):
        slug = defaultfilters.slugify(name)
        slug_num = slug
        n = 2
        filter_param = '%s__exact' % self.name
        filters = {filter_param: slug_num}
        while objects.filter(**filters):
            slug_num = slug + u'-%s' % n
            filters[filter_param] = slug_num
            n += 1
        return slug_num

    def _get_manager(self, instance):
        instance_model = instance.__class__
        if not self.unique_on_parent_model:
            return instance_model._default_manager
        models_to_iterate = [instance_model] + get_ordered_parents(instance_model)
        for model in models_to_iterate:
            if self in model._meta.local_fields:
                return model._default_manager

    def pre_save(self, instance, add):
        value = getattr(instance, self.autofromfield)

        objects_manager = self._get_manager(instance)

        if not instance.id:
            slug = self.sluggify(value, objects_manager.all())
        elif add or self.force_on_edit:
            slug = self.sluggify(value, objects_manager.exclude(id=instance.id))
        else:
            slug = getattr(instance, self.name)
        setattr(instance, self.name, slug)
        return slug

    def get_internal_type(self):
        return 'SlugField'
