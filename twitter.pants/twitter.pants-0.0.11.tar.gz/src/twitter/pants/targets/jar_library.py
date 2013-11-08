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

from functools import partial

from twitter.common.collections import maybe_list, OrderedSet

from twitter.pants.base import manual, Target
from twitter.pants.base.target import TargetDefinitionException
from twitter.pants.targets.anonymous import AnonymousDeps
from twitter.pants.targets.external_dependency import ExternalDependency


@manual.builddict(tags=["anylang"])
class JarLibrary(Target):
  """Serves as a proxy for one or more JarDependencies or JavaTargets."""

  def __init__(self, name, dependencies):
    """
    :param string name: The name of this module target, addressable via pants via the portion
      of the spec following the colon
    :param dependencies: one or more ``dependencies``, library targets,
      binary targets, or ``pants``.
    """

    Target.__init__(self, name)

    if dependencies is None:
      raise TargetDefinitionException(self, "dependencies are required")
    self.dependencies = OrderedSet(maybe_list(dependencies,
      expected_type=(ExternalDependency, AnonymousDeps, Target),
      raise_type=partial(TargetDefinitionException, self)))

  def resolve(self):
    yield self
    for dependency in self.dependencies:
      for resolved_dependency in dependency.resolve():
        yield resolved_dependency
