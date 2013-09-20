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

from itertools import chain

import jinja2

from .filters import filters as morefilters

all = 'Environment',

class Environment(jinja2.Environment):
  def __init__(self, filters = {}, tests = {}, globals = {}, **kwargs):
    jinja2.Environment.__init__(self, **kwargs)

    for name, func in chain(morefilters.items(), filters.items()):
      self.filters[name] = func

    for name, func in tests.items():
      self.tests[name] = func

    for name, value in globals.items():
      self.globals[name] = value
