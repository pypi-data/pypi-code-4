# ==================================================================================================
# Copyright 2012 Twitter, Inc.
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

from twitter.common.dirutil import Fileset
from twitter.common.lang import Compatibility
from twitter.pants import is_concrete
from twitter.pants.base import manual, TargetDefinitionException

from .internal import InternalTarget
from .jvm_target import JvmTarget
from .resources import Resources


@manual.builddict(tags=["jvm"])
class JvmBinary(JvmTarget):
  """Produces a JVM binary optionally identifying a launcher main class.

  Invoking the ``binary`` goal on one of these targets creates a binary jar;
  the ``run`` goal executes it.

  If a ``main`` is specified, the binary can collect the main class from an
  depended-upon library source file, from a transitive dependency, or from a
  source specified in the ``source`` parameter.
  """
  def __init__(self, name,
               main=None,
               basename=None,
               source=None,
               resources=None,
               dependencies=None,
               excludes=None,
               deploy_excludes=None,
               configurations=None):
    """
    :param string name: The name of this target, which combined with this
      build file defines the target :class:`twitter.pants.base.address.Address`.
    :param string main: The name of the ``main`` class, e.g.,
      ``'com.twitter.common.examples.pingpong.Main'``.
    :param string basename: Base name for the generated ``.jar`` file, e.g.,
      ``'pingpong'``. (By default, uses ``name`` param)
    :param string source: Name of one ``.java`` or ``.scala`` file (a good
      place for a ``main``).
    :param resources: List of ``resource``\s to include in bundle.
    :param dependencies: List of targets (probably ``java_library`` and
     ``scala_library`` targets) to "link" in.
    :param excludes: List of ``exclude``\s to filter this target's transitive
     dependencies against.
    :param deploy_excludes: List of ``excludes`` to apply at deploy time.
      If you, for example, deploy a java servlet that has one version of
      ``servlet.jar`` onto a Tomcat environment that provides another version,
      they might conflict. ``deploy_excludes`` gives you a way to build your
      code but exclude the conflicting ``jar`` when deploying.
    :param configurations: Ivy configurations to resolve for this target.
      This parameter is not intended for general use.
    :type configurations: tuple of strings
    """
    JvmTarget.__init__(self,
                       name=name,
                       sources=[source] if source else None,
                       dependencies=dependencies,
                       excludes=excludes,
                       configurations=configurations)

    if main and not isinstance(main, Compatibility.string):
      raise TargetDefinitionException(self, 'main must be a fully qualified classname')

    if source and not isinstance(source, Compatibility.string):
      raise TargetDefinitionException(self, 'source must be a single relative file path')

    self.main = main
    self.basename = basename or name
    self.resources = list(self.resolve_all(resources, Resources))
    self.deploy_excludes = deploy_excludes or []


class RelativeToMapper(object):
  """A mapper that maps files specified relative to a base directory."""

  def __init__(self, base):
    """The base directory files should be mapped from."""

    self.base = base

  def __call__(self, file):
    return os.path.relpath(file, self.base)

  def __repr__(self):
    return 'IdentityMapper(%s)' % self.base


@manual.builddict(tags=["jvm"])
class Bundle(object):
  """Defines a bundle of files mapped from their full path name to a path name in the bundle."""

  def __init__(self, mapper=None, relative_to=None):
    """Creates a new bundle with an empty filemap.

    To add files, call the result's ``add`` method, passing in ``globs``,
    ``rglobs``, or paths. E.g., ``bundles = [ bundle().add(rglobs('config/*', 'scripts/*')) ]``.

    :param mapper: Function that takes a path string and returns a path string. Takes a path in
      the source tree, returns a path to use in the resulting bundle. By default, an identity mapper.
    :param string relative_to: Set up a simple mapping from source path to bundle path.
      E.g., ``bundle(relative_to='foo').add(rglobs('foo/bin/*'))`` to have those files show up
      in the bundle under ``bin`` instead of ``foo/bin``.
    """
    if mapper and relative_to:
      raise ValueError("Must specify exactly one of 'mapper' or 'relative_to'")

    if relative_to:
      base = os.path.abspath(relative_to)
      if not os.path.isdir(base):
        raise ValueError('Could not find a directory to bundle relative to at %s' % base)
      self.mapper = RelativeToMapper(base)
    else:
      self.mapper = mapper or RelativeToMapper(os.getcwd())

    self.filemap = {}

  @manual.builddict()
  def add(self, *filesets):
    for fileset in filesets:
      paths = fileset() if isinstance(fileset, Fileset) \
                        else fileset if hasattr(fileset, '__iter__') \
                        else [fileset]
      self.filemap.update(((os.path.abspath(path), self.mapper(path)) for path in paths))
    return self

  def resolve(self):
    yield self

  def __repr__(self):
    return 'Bundle(%s, %s)' % (self.mapper, self.filemap)


@manual.builddict(tags=["jvm"])
class JvmApp(InternalTarget):
  """Defines a jvm app package consisting of a binary plus additional bundles of files.

  Useful if you're building a service that you'll deploy to some other machine;
  that is, you're not just building a runnable binary, but also its data files.
  """

  def __init__(self, name, binary, bundles, basename=None):
    InternalTarget.__init__(self, name, dependencies=[binary])

    if not binary:
      raise TargetDefinitionException(self, 'binary is required')
    if not bundles:
      raise TargetDefinitionException(self, 'bundles must be specified')

    self._binary = binary
    self._bundles = bundles
    self.basename = basename or name

    self._resolved_binary = None
    self._resolved_bundles = []

  @property
  def binary(self):
    self._maybe_resolve_binary()
    return self._resolved_binary

  def _maybe_resolve_binary(self):
    if self._binary is not None:
      binaries = list(filter(is_concrete, self._binary.resolve()))
      if len(binaries) != 1 or not isinstance(binaries[0], JvmBinary):
        raise TargetDefinitionException(self,
                                        'must supply exactly 1 JvmBinary, got %s' % self._binary)
      self._resolved_binary = binaries[0]
      self._binary = None

  @property
  def bundles(self):
    self._maybe_resolve_bundles()
    return self._resolved_bundles

  def _maybe_resolve_bundles(self):
    if self._bundles is not None:
      def is_resolvable(item):
        return hasattr(item, 'resolve')

      def is_bundle(bundle):
        return isinstance(bundle, Bundle)

      def resolve(item):
        return list(item.resolve()) if is_resolvable(item) else [None]

      if is_resolvable(self._bundles):
        self._bundles = resolve(self._bundles)

      try:
        for item in iter(self._bundles):
          for bundle in resolve(item):
            if not is_bundle(bundle):
              raise TypeError()
            self._resolved_bundles.append(bundle)
      except TypeError:
        raise TargetDefinitionException(self, 'bundles must be one or more Bundle objects, '
                                              'got %s' % self._bundles)
      self._bundles = None



