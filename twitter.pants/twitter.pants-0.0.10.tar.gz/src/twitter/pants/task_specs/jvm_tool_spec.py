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

from __future__ import print_function

__author__ = "tdesai"

from twitter.pants.goal.jvm_tool_goal import JvmToolGoal
from twitter.pants.tasks.jvm_tool_task import JvmToolTask
from twitter.pants.task_specs.arguments import JvmProperty
from twitter.pants.task_specs.nailgun_task_spec_with_jar_deps import NailgunTaskSpecWithJarDeps


class JvmToolSpec(NailgunTaskSpecWithJarDeps):

  def __init__(self,
               name,
               main,
               sources,
               args,
               dependencies,
               ng_daemon=None,
               options=None,
               description='',
               phase_dependencies=None):
    super(JvmToolSpec, self).__init__(name=name,
                                      main=main,
                                      sources=sources,
                                      args=args,
                                      dependencies=dependencies,
                                      ng_daemon=ng_daemon,
                                      options=options,
                                      description=description,
                                      phase_dependencies=phase_dependencies)
    goal = JvmToolGoal(name=name, action=JvmToolTask, jvm_tool_spec=self,
                       dependencies=phase_dependencies)
    phase = goal.install()
    if description:
      phase.with_description(description)

  def _add_default_options(self):
    skip_tool_option = {'dest': '_'.join([self._name, 'skip']),
                        'name': 'skip',
                        'default': False,
                        'help': 'Skip %s' % self._name}
    self._options.append(skip_tool_option)

  def get_args(self, config):
    args = {'jvmargs': [],
            'opts': []}
    for arg in self._args:
      key = 'jvmargs' if isinstance(arg, JvmProperty) else 'opts'
      args[key].extend(arg.get(config))
    return args
