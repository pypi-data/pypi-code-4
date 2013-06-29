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
from player.block import Block, register_block

from news.models import NewsItem


class NewsBlock(Block):
    name = 'newsblock'
    label = _('Latest news block')
    config_params = (
        params.PositiveInteger(
            name='limit',
            label=_('number of news for the "Latest news" block'),
            default=5,
        ),
    )

    def render(self, request, context):
        limit = self.get_config()['limit'].get_value()
        news_list = NewsItem.objects.all()[:limit]
        context.update({
            'news_list': news_list,
        })
        return self.render_block(
            request,
            template_name='news/news_block.html',
            context=context,
        )

register_block(NewsBlock)
