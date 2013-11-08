# ==================================================================================================
# Copyright 2013 Twitter, Inc.
# --------------------------------------------------------------------------------------------------
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this work except in compliance with the License.
# You may obtain a copy of the License in the LICENSE file, or at:
#
#  http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==================================================================================================

import os

from twitter.pants import binary_util, is_codegen, is_java
from twitter.pants.task_specs.arguments import ArgError
from twitter.pants.tasks import TaskError
from twitter.pants.tasks.nailgun_task import NailgunTask


DEFAULT_CONFS = ['default']


def _is_checked(target):
  return is_java(target) and not is_codegen(target)


class JvmToolTask(NailgunTask):

  @classmethod
  def setup_parser(cls, option_group, args, mkflag, options):
    NailgunTask.setup_parser(option_group, args, mkflag)
    for option in options:
      option_group.add_option(mkflag(option['name']),
                              mkflag(option['name'], negate=True),
                              dest=option['dest'],
                              default=option['default'],
                              action='callback', callback=mkflag.set_bool,
                              help=option['help'])

  def __init__(self, context, jvm_tool_spec):
    self._jvm_tool_spec = jvm_tool_spec
    self._name = jvm_tool_spec.name
    self.__class__.__name__ = self._name
    self._workdir = context.config.get(
                      self._name, 'workdir',
                      default=os.path.join(context.config.getdefault('homedir'),
                                           '.pants.d',
                                           self._name))
    self._confs = context.config.getlist(self._name, 'confs', default=DEFAULT_CONFS)
    self._log = context.log
    super(JvmToolTask, self).__init__(context, use_daemon=jvm_tool_spec.ng_daemon)

  def execute(self, targets):
    try:
      if not getattr(self.context.options, '_'.join((self._name, "skip"))):
        with self.changed(filter(_is_checked, targets)) as changed_targets:
          sources = self._calculate_sources(changed_targets)
          if sources:
            result = self._run_tool(sources)
            if result != 0:
              raise TaskError('java %s ... exited non-zero (%i)' % (self._jvm_tool_spec.main,
                                                                    result))
    except ArgError as ae:
      self._log.info("%s" % ae)
      raise TaskError('Arguments specified to tool are incorrect.\n%s' % ae)

  def _calculate_sources(self, targets):
    sources = set()
    for target in targets:
      for suffix in self._jvm_tool_spec.sources:
        sources.update([os.path.join(target.target_base, source)
                        for source in target.sources if source.endswith(suffix)])
    return sources

  def _run_tool(self, sources):
    classpath = binary_util.get_tool_classpath(tool_lib_dir=os.path.join(self._workdir, 'lib'))
    with self.context.state('classpath', []) as cp:
      classpath.extend(jar for conf, jar in cp if conf in self._confs)
    args = self._jvm_tool_spec.get_args(self.context.config)
    return self.runjava(main=self._jvm_tool_spec.main,
                        classpath=classpath,
                        opts=args['opts'],
                        jvmargs=args['jvmargs'],
                        args=sources)
