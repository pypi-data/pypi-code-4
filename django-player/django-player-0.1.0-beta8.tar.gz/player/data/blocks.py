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

from django.utils.translation import ugettext_lazy as _

from configfield import params
from player.block import Block, TemplateBlock, register_block
from player.data.params import CollectionParam


class CollectionBlock(Block):
    config_params = Block.config_params + (
        CollectionParam(
            name='collection',
            label=_('Collection to be used (write the slug)'),
        ),
        params.Integer(
            name='limit',
            label=_('number of items shown (set -1 for infinite)'),
            default=-1,
        ),
    )

    def update_context(self, context):
        collection = self.get_config()['collection'].get_value()
        limit = self.get_config()['limit'].get_value()
        item_list = collection.item_set.all()
        if limit >= 0:
            item_list = item_list[:limit]
        context.update({'item_list': item_list})


class TemplateCollectionBlock(TemplateBlock, CollectionBlock):
    name = 'templatecollectionblock'
    label = _('Template collection block')
    config_params = TemplateBlock.config_params + CollectionBlock.config_params


register_block(TemplateCollectionBlock)
