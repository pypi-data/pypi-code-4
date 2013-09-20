# jinja-tools
#
# Various tools for Jinja2,
# including new filters and tests based on python-moretools,
# a JinjaLoader class for Django,
# and a simple JinjaBuilder class for SCons.
#
# Copyright (C) 2011-2013 Stefan Zimmermann <zimmermann.code@gmail.com>
#
# jinja-tools is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# jinja-tools is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with jinja-tools.  If not, see <http://www.gnu.org/licenses/>.

from jinja2.ext import Extension
from jinja2.nodes import CallBlock

class TagExtensionMeta(type(Extension)):
    def __new__(cls, clsname, bases, clsattrs):
        tagtree = {}
        for name in clsattrs:
            if name.startswith('tag_'):
                level = tagtree
                for tag in name.split('_')[1:]:
                    level = level.setdefault(tag, {})

        clsattrs['tags'] = set(tagtree)
        cls = type(Extension).__new__(cls, clsname, bases, clsattrs)

        def parse_subtags(self, tag, parser):
            level = tagtree[tag]
            subtags = []
            while level:
                token = parser.stream.current
                if token.type != 'name':
                    break
                try:
                    level = level[token.value]
                except KeyError:
                    break

                subtags.append(token.value)
                parser.stream.skip()

            return subtags

        cls._parse_subtags = parse_subtags
        return cls

class TagExtension(Extension):
    __metaclass__ = TagExtensionMeta

    def parse(self, parser):
        tag = parser.stream.current.value
        parser.stream.next()

        subtags = self._parse_subtags(tag, parser)
        methodname = 'tag_' + tag
        if subtags:
            methodname += '_' + '_'.join(subtags)

        lineno = parser.stream.current.lineno
        content = parser.parse_statements(
          ['name:end' + tag], drop_needle=True)
        node = CallBlock(self.call_method(methodname), [], [], content)
        node.set_lineno(lineno)
        return node
