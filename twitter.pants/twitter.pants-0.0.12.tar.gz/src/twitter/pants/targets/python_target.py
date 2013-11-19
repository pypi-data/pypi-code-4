# ==================================================================================================
# Copyright 2011 Twitter, Inc.
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

from twitter.common.collections import OrderedSet
from twitter.common.python.interpreter import PythonIdentity
from twitter.pants.base import Target
from twitter.pants.base.target import TargetDefinitionException
from twitter.pants.targets.with_sources import TargetWithSources


class PythonTarget(TargetWithSources):
  """Base class for all Python targets."""

  def __init__(self,
               name,
               sources,
               resources=None,
               dependencies=None,
               provides=None,
               compatibility=None):
    TargetWithSources.__init__(self, name, sources=sources)
    self.resources = self._resolve_paths(self.target_base, resources) if resources else OrderedSet()
    self.dependencies = OrderedSet(dependencies) if dependencies else OrderedSet()
    self.provides = provides
    self.compatibility = compatibility or ['']
    for req in self.compatibility:
      try:
        PythonIdentity.parse_requirement(req)
      except ValueError as e:
        raise TargetDefinitionException(str(e))

  def _walk(self, walked, work, predicate=None):
    Target._walk(self, walked, work, predicate)
    for dependency in self.dependencies:
      for dep in dependency.resolve():
        if isinstance(dep, Target) and not dep in walked:
          walked.add(dep)
          if not predicate or predicate(dep):
            additional_targets = work(dep)
            dep._walk(walked, work, predicate)
            if additional_targets:
              for additional_target in additional_targets:
                if hasattr(additional_target, '_walk'):
                  additional_target._walk(walked, work, predicate)
