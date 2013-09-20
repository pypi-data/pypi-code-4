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

from SCons.Builder import BuilderBase
from SCons.Action import Action

import jinjatools

__all__ = 'JinjaBuilder',

class JinjaBuilder(BuilderBase):
  def __init__(self, jinja_loader, context = {}):
    BuilderBase.__init__(
      self, action = Action(self.jinja_action),
      src_suffix = '.jinja', suffix = '')

    self.jinja_env = jinjatools.Environment(loader = jinja_loader)
    self.jinja_template_context = context

  def jinja_action(self, target, source, env):
    context = dict(self.jinja_template_context)
    try:
      context.update(env['JINJACONTEXT'])
    except KeyError:
      pass

    options = {}
    try:
      options['loader'] = env['JINJALOADER']
    except KeyError:
      pass
    overlay = self.jinja_env.overlay(**options)
    template = overlay.get_template(str(source[0]))

    targetfile = open(str(target[0]), 'w')
    targetfile.write(template.render(context).encode('utf-8'))
    targetfile.close()

  jinja_action.func_name = 'Jinja'
