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
__author__ = "tdesai"

from twitter.common.collections import maybe_list
from twitter.pants.targets.jar_dependency import JarDependency
from twitter.pants.task_specs import TaskSpec, TaskSpecError


class NailgunTaskSpecWithJarDeps(TaskSpec):
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
    super(NailgunTaskSpecWithJarDeps, self).__init__(name=name,
                                                     sources=sources,
                                                     args=args,
                                                     options=options,
                                                     phase_dependencies=phase_dependencies,
                                                     description=description)
    self._main = main
    self._ng_daemon = ng_daemon
    self._dependencies = maybe_list(dependencies, JarDependency, TaskSpecError)

  @property
  def dependencies(self):
    return self._dependencies

  @property
  def main(self):
    return self._main

  @property
  def ng_daemon(self):
    return self._ng_daemon
