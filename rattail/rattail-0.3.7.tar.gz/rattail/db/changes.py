#!/usr/bin/env python
# -*- coding: utf-8  -*-
################################################################################
#
#  Rattail -- Retail Software Framework
#  Copyright © 2010-2012 Lance Edgar
#
#  This file is part of Rattail.
#
#  Rattail is free software: you can redistribute it and/or modify it under the
#  terms of the GNU Affero General Public License as published by the Free
#  Software Foundation, either version 3 of the License, or (at your option)
#  any later version.
#
#  Rattail is distributed in the hope that it will be useful, but WITHOUT ANY
#  WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
#  FOR A PARTICULAR PURPOSE.  See the GNU Affero General Public License for
#  more details.
#
#  You should have received a copy of the GNU Affero General Public License
#  along with Rattail.  If not, see <http://www.gnu.org/licenses/>.
#
################################################################################

"""
Data Changes
"""

from sqlalchemy.event import listen
from sqlalchemy.orm import object_mapper, RelationshipProperty

from .model import Change, Batch, BatchColumn, BatchRow, Role, UserRole
from ..core import get_uuid


__all__ = ['record_changes']


import logging
log = logging.getLogger(__name__)


def record_changes(session, ignore_role_changes=True):
    """
    Record all changes which occur within a session.

    :param session: A ``sqlalchemy.orm.sessionmaker`` class, or an instance
       thereof.

    :param ignore_role_changes: Whether changes involving roles and role
       membership should be ignored.  This defaults to ``True``, which means
       each database will be responsible for maintaining its own role (and by
       extension, permissions) data.
    """

    listen(session, 'before_flush', ChangeRecorder(ignore_role_changes))


class ChangeRecorder(object):
    """
    Listener for session ``before_flush`` events.

    This class is responsible for adding stub records to the ``changes`` table,
    which will in turn be used by the database synchronizer to manage change
    data propagation.
    """

    def __init__(self, ignore_role_changes=True):
        self.ignore_role_changes = ignore_role_changes

    def __call__(self, session, flush_context, instances):
        """
        Method invoked when session ``before_flush`` event occurs.
        """

        for instance in session.deleted:
            log.debug("ChangeRecorder: found deleted instance: {0}".format(repr(instance)))
            self.record_change(session, instance, deleted=True)
        for instance in session.new:
            log.debug("ChangeRecorder: found new instance: {0}".format(repr(instance)))
            self.record_change(session, instance)
        for instance in session.dirty:
            if session.is_modified(instance, passive=True):
                log.debug("ChangeRecorder: found dirty instance: {0}".format(repr(instance)))
                self.record_change(session, instance)

    def record_change(self, session, instance, deleted=False):
        """
        Record a change record in the database.

        If ``instance`` represents a change in which we are interested, then
        this method will create (or update) a :class:`rattail.db.model.Change`
        record.

        :returns: ``True`` if a change was recorded, or ``False`` if it was
           ignored.
        """

        # No need to record changes for changes.  Must not use `isinstance()`
        # here due to mocking in tests.
        if (hasattr(instance.__class__, '__tablename__')
            and instance.__class__.__tablename__ == 'changes'):
            return False

        # No need to record changes for batch data.
        if isinstance(instance, (Batch, BatchColumn, BatchRow)):
            return False

        # Ignore instances which don't use UUID.
        if not hasattr(instance, 'uuid'):
            return False

        # Ignore Role instances, if so configured.
        if self.ignore_role_changes and isinstance(instance, (Role, UserRole)):
            return False

        # Provide an UUID value, if necessary.
        self.ensure_uuid(instance)

        # Record the change.
        change = session.query(Change).get(
            (instance.__class__.__name__, instance.uuid))
        if not change:
            change = Change(
                class_name=instance.__class__.__name__,
                uuid=instance.uuid)
            session.add(change)
        change.deleted = deleted
        log.debug("ChangeRecorder.record_change: recorded change: %s" % repr(change))
        return True

    def ensure_uuid(self, instance):
        """
        Ensure the given instance has a UUID value.

        This uses the following logic:

        * If the instance already has a UUID, nothing will be done.

        * If the instance contains a foreign key to another table, then that
          relationship will be traversed and the foreign object's UUID will be used
          to populate that of the instance.

        * Otherwise, a new UUID will be generated for the instance.
        """

        if instance.uuid:
            return

        mapper = object_mapper(instance)
        if not mapper.columns['uuid'].foreign_keys:
            instance.uuid = get_uuid()
            return

        for prop in mapper.iterate_properties:
            if (isinstance(prop, RelationshipProperty)
                and len(prop.remote_side) == 1
                and list(prop.remote_side)[0].key == 'uuid'):

                foreign_instance = getattr(instance, prop.key)
                if foreign_instance:
                    self.ensure_uuid(foreign_instance)
                    instance.uuid = foreign_instance.uuid
                    return

        instance.uuid = get_uuid()
        log.error("ChangeRecorder.ensure_uuid: unexpected scenario; generated new UUID for instance: {0}".format(repr(instance)))
