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

from django.core import urlresolvers

import jinjatools

all = 'JinjaLoader',

class Template(object):
  def __init__(self, template):
    self.template = template

  def render(self, context):
    dicts = context.dicts
    context = {}
    for d in dicts:
      context.update(d)

    return self.template.render(context)

class Django(object):
    def url(self, name):
        return urlresolvers.reverse(name)

class LoaderFactory(object):
  def __getitem__(self, DjangoLoader):
    class JinjaLoader(DjangoLoader):
      def __init__(
        self, jinja_loader, filters = {}, tests = {}, globals = {},
        **kwargs
        ):
        DjangoLoader.__init__(self)

        globals = dict(globals)
        globals.update(
          django=Django(),
          )
        self.jinja_env = jinjatools.Environment(
          loader = jinja_loader,
          filters = filters, tests = tests, globals = globals)

      def load_template(self, name, dirs):
        if name.startswith('jinja:'):
          name = name.split('jinja:', 1)[1]
          source, origin = self.load_template_source(name, dirs)
          return (
            Template(self.jinja_env.from_string(source)),
            origin)

        return DjangoLoader.load_template(self, name, dirs)

    return JinjaLoader

JinjaLoader = LoaderFactory()
