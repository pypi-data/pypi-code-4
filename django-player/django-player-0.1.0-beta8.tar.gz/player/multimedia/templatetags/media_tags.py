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

import time

from django import template
from django.core.cache import cache

from classytags.arguments import Argument
from classytags.core import Tag, Options
from classytags.parser import Parser
from compressor import CssCompressor, JsCompressor
from compressor.conf.settings import COMPRESS

register = template.Library()


MINT_DELAY = 30  # on how long any compression should take to be generated
REBUILD_TIMEOUT = 2592000  # rebuilds the cache every 30 days if nothing has changed


class MediaParser(Parser):

    def parse_blocks(self):
        super(MediaParser, self).parse_blocks()
        self.blocks['nodelist'] = self.parser.parse()


class RenderBundledMedia(Tag):
    name = 'render_bundled_media'

    options = Options(
        Argument('name'),
        parser_class=MediaParser,
    )

    def cache_get(self, key):
        packed_val = cache.get(key)
        if packed_val is None:
            return None
        val, refresh_time, refreshed = packed_val
        if (time.time() > refresh_time) and not refreshed:
            # Store the stale value while the cache
            # revalidates for another MINT_DELAY seconds.
            self.cache_set(key, val, timeout=MINT_DELAY, refreshed=True)
            return None
        return val

    def cache_set(self, key, val, timeout=REBUILD_TIMEOUT, refreshed=False):
        refresh_time = timeout + time.time()
        real_timeout = timeout + MINT_DELAY
        packed_val = (val, refresh_time, refreshed)
        return cache.set(key, packed_val, real_timeout)

    @property
    def nodelist(self):
        return self.blocks['nodelist']

    def render_tag(self, context, name, nodelist):
        request = context['request']
        rendered_contents = nodelist.render(context)
        content = request.media_holder[name].render()
        if COMPRESS:
            if name == 'css':
                compressor = CssCompressor(content)
            elif name == 'js':
                compressor = JsCompressor(content)
            output = self.cache_get(compressor.cachekey)
            if output is None:
                try:
                    output = compressor.output()
                    self.cache_set(compressor.cachekey, output)
                except:
                    from traceback import format_exc
                    raise Exception(format_exc())
        else:
            output = content  # no compression
        return '%s\n%s' % (output, rendered_contents)

register.tag(RenderBundledMedia)


class AddMediaParser(Parser):

    def parse_blocks(self):
        name = self.kwargs['name'].var.token
        self.blocks['nodelist'] = self.parser.parse(
            ('endaddmedia', 'endaddmedia %s' % name)
        )
        self.parser.delete_first_token()


class AddMedia(Tag):
    name = 'addmedia'
    options = Options(
        Argument('name'),
        parser_class=AddMediaParser,
    )

    def render_tag(self, context, name, nodelist):
        request = context['request']
        rendered_contents = nodelist.render(context)
        request.media_holder[name].append(rendered_contents)
        return ""

register.tag(AddMedia)
