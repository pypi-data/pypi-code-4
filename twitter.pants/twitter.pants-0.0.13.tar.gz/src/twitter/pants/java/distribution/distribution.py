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

from contextlib import contextmanager

import os
import pkgutil
import subprocess

from twitter.common import log
from twitter.common.contextutil import temporary_dir
from twitter.common.decorators import lru_cache
from twitter.common.lang import Compatibility

from twitter.pants.base.revision import Revision


class Distribution(object):
  """Represents a java distribution - either a JRE or a JDK installed on the local system.

  In particular provides access to the distribution's binaries; ie: java while ensuring basic
  constraints are met.  For example a minimum version can be specified if you know need to compile
  source code or run bytecode that exercise features only available in that version forward.
  """

  class Error(Exception):
    """Indicates an invalid java distribution."""

  @classmethod
  @lru_cache(maxsize=None)
  def locate(cls, minimum_version=None, jdk=False):
    """Finds a java distribution that meets any given constraints and returns it.

    First looks in JDK_HOME and JAVA_HOME if defined falling back to a search on the PATH.
    Raises Distribution.Error if no suitable java distribution could be found.
    """
    def home_bin_path(home_env_var):
      home = os.environ.get(home_env_var)
      return os.path.join(home, 'bin') if home else None

    def search_path():
      yield home_bin_path('JDK_HOME')
      yield home_bin_path('JAVA_HOME')
      path = os.environ.get('PATH')
      if path:
        for p in path.strip().split(os.pathsep):
          yield p

    for path in filter(None, search_path()):
      try:
        dist = cls(path, minimum_version=minimum_version, jdk=jdk)
        dist.validate()
        log.debug('Located %s for constraints: minimum_version'
                  ' %s, jdk %s' % (dist, minimum_version, jdk))
        return dist
      except (ValueError, cls.Error):
        pass

    raise cls.Error('Failed to locate a %s distribution with minimum_version %s'
                    % ('JDK' if jdk else 'JRE', minimum_version))

  @staticmethod
  def _parse_java_version(version):
    # Java version strings have been well defined since release 1.3.1 as defined here:
    #  http://www.oracle.com/technetwork/java/javase/versioning-naming-139433.html
    # These version strings comply with semver except that the traditional pre-release semver
    # slot (the 4th) can be delimited by an _ in the case of update releases of the jdk.
    # We accomodate that difference here.
    return Revision.semver(version.replace('_', '-'))

  @staticmethod
  def _is_executable(path):
    return os.path.isfile(path) and os.access(path, os.X_OK)

  def __init__(self, bin_path='/usr/bin', minimum_version=None, jdk=False):
    """Creates a distribution wrapping the given bin_path.

    :param string bin_path: the path to the java distributions bin dir
    :param minimum_version: a modified semantic version string or else a Revision object
    :param bool jdk: ``True`` to require the distribution be a JDK vs a JRE
    """

    if not os.path.isdir(bin_path):
      raise ValueError('The specified distribution path is invalid: %s' % bin_path)
    self._bin_path = bin_path

    if isinstance(minimum_version, Compatibility.string):
      minimum_version = self._parse_java_version(minimum_version)
    if minimum_version and not isinstance(minimum_version, Revision):
      raise ValueError('minimum_version must be a string or a Revision object,'
                       ' given: %s' % minimum_version)
    self._minimum_version = minimum_version

    self._jdk = jdk
    self._validated = {}

  @property
  def java(self):
    """Returns the path to this distribution's java command.

    If this distribution has no valid java command raises Distribution.Error."
    """
    return self.binary('java')

  def binary(self, name):
    """Returns the path to the command of the given name for this distribution.

    For example: ::

        >>> d = Distribution()
        >>> jar = d.binary('jar')
        >>> jar
        '/usr/bin/jar'
        >>>

    If this distribution has no valid command of the given name raises Distribution.Error."
    """
    if not isinstance(name, Compatibility.string):
      raise ValueError('name must be a binary name, given %s of type %s' % (name, type(name)))
    self.validate()
    return self._validated_executable(name)

  def validate(self):
    """Validates this distribution against its configured constraints.

    Raises Distribution.Error if this distribution is not valid according to the configured
    constraints.
    """
    if self._validated:
      return

    with self._valid_executable('java') as java:
      if self._minimum_version:
        with temporary_dir() as classpath:
          with open(os.path.join(classpath, 'Version.class'), 'w+') as fp:
            fp.write(pkgutil.get_data(__name__, 'Version.class'))
          cmd = [java, '-cp', classpath, 'Version']
          process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
          stdout, stderr = process.communicate()
          if process.returncode != 0:
            raise self.Error('Failed to determine java version for %s with %s - exit code'
                             ' %d: %s' % (java, ' '.join(cmd), process.returncode, stderr))
          version = self._parse_java_version(stdout.strip())
          if version < self._minimum_version:
            raise self.Error('The java distribution at %s is too old; expecting at least %s and'
                             ' got %s' % (java, self._minimum_version, version))

    if self._jdk:
      self._validated_executable('javac')  # Calling purely for the check and cache side effects

  def _validate_executable(self, name):
    exe = os.path.join(self._bin_path, name)
    if not self._is_executable(exe):
      raise self.Error('Failed to locate the %s executable, %s does not appear to be a'
                       ' valid %s distribution' % (name, self, 'JDK' if self._jdk else 'JRE'))
    return exe

  def _validated_executable(self, name):
    exe = self._validated.get(name)
    if not exe:
      exe = self._validate_executable(name)
      self._validated[name] = exe
    return exe

  @contextmanager
  def _valid_executable(self, name):
    exe = self._validate_executable(name)
    yield exe
    self._validated[name] = exe

  def __repr__(self):
    return 'Distribution(%r, minimum_version=%r, jdk=%r)' % (self._bin_path, self._minimum_version,
                                                             self._jdk)
