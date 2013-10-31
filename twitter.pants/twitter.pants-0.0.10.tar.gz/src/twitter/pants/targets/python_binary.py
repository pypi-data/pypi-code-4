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

import sys

from twitter.common.collections import maybe_list
from twitter.common.lang import Compatibility
from twitter.common.python.pex_info import PexInfo
from twitter.common.python.platforms import Platform

from twitter.pants.base import manual, TargetDefinitionException
from twitter.pants.base.build_info import get_build_info
from .python_target import PythonTarget


@manual.builddict(tags=["python"])
class PythonBinary(PythonTarget):
  """Produces a Python binary.

  Python binaries are pex files, self-contained executable shell
  scripts that contain a complete Python environment capable of
  running the target. For more information about pex files see
  https://github.com/twitter/commons/blob/master/src/python/twitter/pants/python/README.md"""

  def __init__(self,
               name,
               source=None,
               dependencies=None,
               entry_point=None,
               inherit_path=False,
               zip_safe=True,
               always_write_cache=False,
               repositories=None,
               indices=None,
               ignore_errors=False,
               allow_pypi=False,
               platforms=(),
               compatibility=None):
    """
    :param name: target name
    :param source: the python source file that becomes this binary's __main__.
      If None specified, drops into an interpreter by default.
    :param dependencies: List of :class:`twitter.pants.base.target.Target` instances
      this target depends on.
    :type dependencies: list of targets
    :param entry_point: the default entry point for this binary.  if None, drops into the entry
      point that is defined by source
    :param inherit_path: inherit the sys.path of the environment that this binary runs in
    :param zip_safe: whether or not this binary is safe to run in compacted (zip-file) form
    :param always_write_cache: whether or not the .deps cache of this PEX file should always
      be written to disk.
    :param repositories: a list of repositories to query for dependencies.
    :param indices: a list of indices to use for packages.
    :param platforms: extra platforms to target when building this binary.
    :param compatibility: either a string or list of strings that represents
      interpreter compatibility for this target, using the Requirement-style format,
      e.g. ``'CPython>=3', or just ['>=2.7','<3']`` for requirements agnostic to interpreter class.
    """
    if source is None and dependencies is None:
      raise TargetDefinitionException(
          'ERROR: no source or dependencies declared for target %s' % name)
    if source and entry_point:
      raise TargetDefinitionException(
          'Can only declare an entry_point if no source binary is specified.')
    if not isinstance(platforms, (list, tuple)) and not isinstance(platforms, Compatibility.string):
      raise TargetDefinitionException('platforms must be a list, tuple or string.')

    self._entry_point = entry_point
    self._inherit_path = bool(inherit_path)
    self._zip_safe = bool(zip_safe)
    self._always_write_cache = bool(always_write_cache)
    self._repositories = maybe_list(repositories or [])
    self._indices = maybe_list(indices or [])
    self._ignore_errors = bool(ignore_errors)
    self._platforms = tuple(maybe_list(platforms or []))

    PythonTarget.__init__(self, name, [] if source is None else [source],
                          compatibility=compatibility,
                          dependencies=dependencies)

  @property
  def platforms(self):
    return self._platforms

  # TODO(wickman) These should likely be attributes on PythonLibrary targets
  # and not PythonBinary targets, or at the very worst, both.
  @property
  def repositories(self):
    return self._repositories

  @property
  def indices(self):
    return self._indices

  @property
  def entry_point(self):
    return self._entry_point

  @property
  def pexinfo(self):
    info = PexInfo.default()
    info.build_properties = get_build_info()._asdict()
    for repo in self._repositories:
      info.add_repository(repo)
    for index in self._indices:
      info.add_index(index)
    info.zip_safe = self._zip_safe
    info.always_write_cache = self._always_write_cache
    info.inherit_path = self._inherit_path
    info.entry_point = self._entry_point
    info.ignore_errors = self._ignore_errors
    return info
