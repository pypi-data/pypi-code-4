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

import os
import collections

from twitter.common.collections import OrderedSet, maybe_list
from twitter.common.lang import Compatibility

from twitter.pants import is_concrete

from .address import Address
from .build_manual import manual
from .parse_context import ParseContext


class TargetDefinitionException(Exception):
  """Thrown on errors in target definitions."""

  def __init__(self, target, msg):
    address = getattr(target, 'address', None)
    if address is None:
      try:
        location = ParseContext.locate().current_buildfile
      except ParseContext.ContextError:
        location = 'unknown location'
      address = 'unknown target of type %s in %s' % (target.__class__.__name__, location)
    super(Exception, self).__init__('Error with %s: %s' % (address, msg))


@manual.builddict()
class Target(object):
  """The baseclass for all pants targets.

  Handles registration of a target amongst all parsed targets as well as location of the target
  parse context.
  """

  _targets_by_address = None
  _addresses_by_buildfile = None

  @classmethod
  def get_all_addresses(cls, buildfile):
    """Returns all of the target addresses in the specified buildfile if already parsed; otherwise,
    parses the buildfile to find all the addresses it contains and then returns them.
    """
    def lookup():
      if buildfile in cls._addresses_by_buildfile:
        return cls._addresses_by_buildfile[buildfile]
      else:
        return OrderedSet()

    addresses = lookup()
    if addresses:
      return addresses
    else:
      ParseContext(buildfile).parse()
      return lookup()

  @classmethod
  def _clear_all_addresses(cls):
    cls._targets_by_address = {}
    cls._addresses_by_buildfile = collections.defaultdict(OrderedSet)

  @classmethod
  def get(cls, address):
    """Returns the specified module target if already parsed; otherwise, parses the buildfile in the
    context of its parent directory and returns the parsed target.
    """
    def lookup():
      return cls._targets_by_address[address] if address in cls._targets_by_address else None

    target = lookup()
    if target:
      return target
    else:
      ParseContext(address.buildfile).parse()
      return lookup()

  @classmethod
  def resolve_all(cls, targets, *expected_types):
    """Yield the resolved concrete targets checking each is a subclass of one of the expected types
    if specified.
    """
    if targets:
      for target in maybe_list(targets, expected_type=Target):
        for resolved in filter(is_concrete, target.resolve()):
          if expected_types and not isinstance(resolved, expected_types):
            raise TypeError('%s requires types: %s and found %s' % (cls, expected_types, resolved))
          yield resolved

  def __init__(self, name):
    """
    :param string name: The target name.
    """
    if not isinstance(name, Compatibility.string):
      self.address = '%s:%s' % (ParseContext.locate().current_buildfile, str(name))
      raise TargetDefinitionException(self, "Invalid target name: %s" % name)
    self.name = name
    self.is_codegen = False
    self.description = None

    self.address = self._locate()

    # TODO(John Sirois): Transition all references to self.identifier to eliminate id builtin
    # ambiguity
    self.id = self._create_id()

    self._register()

    # For synthetic codegen targets this will be the original target from which
    # the target was synthesized.
    self.derived_from = self

  def _post_construct(self, func, *args, **kwargs):
    """Registers a command to invoke after this target's BUILD file is parsed."""
    ParseContext.locate().on_context_exit(func, *args, **kwargs)

  def _create_id(self):
    """Generates a unique identifier for the BUILD target.

    The generated id is safe for use as a path name on unix systems.
    """
    buildfile_relpath = os.path.dirname(self.address.buildfile.relpath)
    if buildfile_relpath in ('.', ''):
      return self.name
    else:
      return "%s.%s" % (buildfile_relpath.replace(os.sep, '.'), self.name)

  def _locate(self):
    parse_context = ParseContext.locate()
    return Address(parse_context.current_buildfile, self.name)

  def _register(self):
    existing = self._targets_by_address.get(self.address)
    if existing and existing is not self:
      if existing.address.buildfile != self.address.buildfile:
        raise TargetDefinitionException(self, "already defined in a sibling BUILD "
                                              "file: %s" % existing.address.buildfile.relpath)
      else:
        raise TargetDefinitionException(self, "duplicate to %s" % existing)

    self._targets_by_address[self.address] = self
    self._addresses_by_buildfile[self.address.buildfile].add(self.address)

  @property
  def identifier(self):
    """A unique identifier for the BUILD target.

    The generated id is safe for use as a path name on unix systems.
    """
    return self.id

  def resolve(self):
    yield self

  def walk(self, work, predicate=None):
    """Performs a walk of this target's dependency graph visiting each node exactly once.

    If a predicate is supplied it will be used to test each target before handing the target to
    work and descending.  Work can return targets in which case these will be added to the walk
    candidate set if not already walked.
    """
    self._walk(set(), work, predicate)

  def _walk(self, walked, work, predicate=None):
    for target in self.resolve():
      if target not in walked:
        walked.add(target)
        if not predicate or predicate(target):
          additional_targets = work(target)
          if hasattr(target, '_walk'):
            target._walk(walked, work, predicate)
          if additional_targets:
            for additional_target in additional_targets:
              if hasattr(additional_target, '_walk'):
                additional_target._walk(walked, work, predicate)

  @manual.builddict()
  def with_description(self, description):
    """Set a human-readable description of this target."""
    self.description = description
    return self

  def __eq__(self, other):
    return isinstance(other, Target) and self.address == other.address

  def __hash__(self):
    return hash(self.address)

  def __ne__(self, other):
    return not self.__eq__(other)

  def __repr__(self):
    return "%s(%s)" % (type(self).__name__, self.address)

Target._clear_all_addresses()
