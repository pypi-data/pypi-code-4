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

import itertools


class TaskSpecError(Exception):
  """Raised to indicate a given TaskSpec is not valid."""


class TaskSpec(object):

  def __init__(self,
               name,
               sources,
               args,
               options=None,
               description='',
               phase_dependencies=None):
    self._name = name
    self._sources = sources
    self._args = args
    #Todo: For now options is an array of hashes with keys 'dest', 'help', 'default'
    self._options = options or []
    self._description = description
    self._phase_dependencies = phase_dependencies or []
    self._add_default_options()

  def _add_default_options(self):
    return

  @property
  def phase_dependencies(self):
    return self._phase_dependencies

  @property
  def name(self):
    return self._name

  @property
  def options(self):
    return self._options

  def get_args(self, config=None):
    chain = itertools.chain.from_iterable(arg.get(config) for arg in self._args)
    return list(chain)

  @property
  def sources(self):
    return self._sources
