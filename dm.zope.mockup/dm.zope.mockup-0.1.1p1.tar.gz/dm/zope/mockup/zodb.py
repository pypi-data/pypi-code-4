# Copyright (C) 2010 by Dr. Dieter Maurer, Illtalstr. 25, D-66571 Bubach, Germany
# see "LICENSE.txt" for details
"""ZODB related mockups

See ``README.txt`` for documentation.
"""
from persistent import Persistent
from transaction._manager import TransactionManager

from ZODB.Connection import Connection, ObjectWriter
from ZODB.DemoStorage import DemoStorage
from ZODB.DB import DB


class MockupConnection(Connection):
  """mockup connection to facilitate tests checking proper modification registration."""

  def get_state(self, obj):
    assert isinstance(obj, Persistent)
    if obj._p_jar is None: self.add(obj)
    assert obj._p_jar is self
    writer = _MockupObjectWriter(obj)
    return [(sobj, writer.serialize(sobj)) for sobj in writer]

  def verify_state(self, state):
    errors = []
    for obj, old_state in state:
      writer = ObjectWriter(obj)
      if old_state != writer.serialize(obj) and obj._p_changed != True:
        errors.append(obj)
      for new_obj in writer._stack[1:]:
        if new_obj._p_jar is None: self.add(new_obj)
    if errors:
      raise AssertionError('unregistered modifications', errors)

  def emulate_commit(self):
    """create a savepoint in order to emulate a commit."""
    self.transaction_manager.savepoint()

  # work around https://bugs.launchpad.net/zodb/+bug/615758
  def _abort(self):
    for obj in self._added.itervalues(): obj._p_changed = False
    super(MockupConnection, self)._abort()
  


_mockup_connection_singleton = None

def get_mockup_connection():
  global _mockup_connection_singleton
  c = _mockup_connection_singleton
  if c is not None:
    c.transaction_manager.get().abort()
    # ZODB 3.8 used '_opened'; ZODB 3.9 'opened'
    c.opened = c._opened = None # prevent returning to connection pool
    c.close()
  else:
    c = _mockup_connection_singleton = MockupConnection(DB(DemoStorage()))
  c.open(TransactionManager())
  return c


class _MockupObjectWriter(ObjectWriter):
  """``ObjectWriter`` registering any persistent subobject, not just new ones."""
  _seen = None

  def persistent_id(self, obj):
    r = ObjectWriter.persistent_id(self, obj)
    if r is not None and obj not in self._stack:
      seen = self._get_seen()
      if obj._p_oid not in seen:
        self._stack.append(obj)
        seen.add(obj._p_oid)
    return r

  def _get_seen(self):
    seen = self._seen
    if seen is None: seen = self._seen = set()
    return seen
