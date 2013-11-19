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

from twitter.pants.goal import Goal
from twitter.pants.tasks.jvm_tool_task import JvmToolTask
from twitter.pants.tasks.ivy_resolver import IvyResolver


class JvmToolGoal(Goal):
  """
  JvmToolGoal resolves the jvm tool by calling make_runnable in prepare phase.
  """

  def __init__(self, name, action, jvm_tool_spec, group=None, dependencies=None):
    super(JvmToolGoal, self).__init__(name, action, group, dependencies)
    self.jvm_tool_spec = jvm_tool_spec

  def _make_runnable(self, context):
    IvyResolver(context, self.jvm_tool_spec).make_runnable()

  def prepare(self, context):
    self._make_runnable(context)
    return JvmToolTask(context=context, jvm_tool_spec=self.jvm_tool_spec)

  def task_setup_parser(self, group, args, mkflag):
    self._task.setup_parser(option_group=group, args=args, mkflag=mkflag,
                            options=self.jvm_tool_spec.options)
