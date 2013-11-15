#
# Copyright (c) 2010, 2013
#   Adam Tauno Williams <awilliam@whitemice.org>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
import sys
import time
import logging
from sqlalchemy import and_
from exception import NotImplementedException

# Permissions; we use the same flags as IMAP except "v"
#  r = read
#  w = write (modify)
#  l = list
#  d = delete [synonymous with t + x]
#  a = administer
#  k = create [not implemented]
#  t = delete object
#  x = delete container [not implemented]
#  i = insert [not implemented]
#  v = view [?]

COILS_CORE_FULL_PERMISSIONS = set(['r', 'w', 'l', 'd', 'a',
                                   'k', 't', 'x', 'i', 'v', ])


class EntityAccessManager(object):
    """ Calculate the access to an entity in the current context.
        There is no single point of the code more performance critical than
        this object.  The server actually spends most of its time
        right here.
    """
    __DebugOn__ = None
    _F_perfprint = False
    __entity__ = 'undefined'

    def __init__(self, ctx):

        self._implied_time = 0.0
        self._asserted_time = 0.0
        self._revoked_time = 0.0

        # Logger
        if (hasattr(self, '__entity__')):
            if isinstance(self.__entity__, list):
                name = '-'.join([x.lower() for x in self.__entity__])
            else:
                name = self.__entity__.lower()
            self.log = logging.getLogger('access.%s' % name)
        else:
            self.log = logging.getLogger('entityaccessmanager')
            self.log.warn('{0} has no __entity__ attribute'.format(repr(self)))

        # Debug Mode
        if EntityAccessManager.__DebugOn__ is None:
            sd = ctx.server_defaults_manager
            EntityAccessManager.__DebugOn__ = \
                sd.bool_for_default('OGoAccessManagerDebugEnabled')
            self._F_perfprint = \
                sd.bool_for_default('CoilsCommandTimingToStdError')

        self._ctx = ctx

    @property
    def debug(self):
        return EntityAccessManager.__DebugOn__

    def materialize_rights(self, objects=None, ):

        if not objects:
            return {}

        if self._ctx.is_admin:
            if self.debug:
                self.log.debug(
                    'administrative account has all rights to all objects')
            rights = {}
            for entity in objects:
                rights[entity] = set(COILS_CORE_FULL_PERMISSIONS)
            return rights

        start = time.time()
        rights = self.implied_rights(objects)
        self._implied_time += (time.time() - start)

        start = time.time()
        rights = self.asserted_rights(rights)
        self._asserted_time += (time.time() - start)

        start = time.time()
        rights = self.revoked_rights(rights)
        self._revoked_time += (time.time() - start)

        return rights

    def default_rights(self):
        return COILS_CORE_FULL_PERMISSIONS

    def implied_rights(self, objects):
        rights = {}
        for entity in objects:
            rights[entity] = set()
        return rights

    def asserted_rights(self, object_rights):
        for entity, implied in object_rights.items():
            if hasattr(entity, 'acls'):
                asserted = self.get_acls('allowed', entity)
                if 'r' in asserted:
                    asserted.add('l')
                object_rights[entity] = implied.union(asserted)
        return object_rights

    def revoked_rights(self, object_rights):
        '''
        Dimish the rights to the entity that have been explictly denied; this
        denial could be due to either negative/denied ACLs or the presence of
        a lock.  Any EntityAccessManager that overrides this method in a
        derived class should be careful to include the lock check [assuming
        the entity in question is a first-class proper].
        '''
        for entity, asserted in object_rights.items():
            denied = self._ctx.lock_manager.rights_denied_by_lock(entity)
            if hasattr(entity, 'acls'):
                denied.update(self.get_acls('denied', entity))
            object_rights[entity] = asserted.difference(denied)
        return object_rights

    def get_acls(self, action, entity):
        '''
        Return the rights [as a set] allowed or denied [action] to the
        specified entity for the current context.  This will be a summary
        [as as set] of all the ACLs that intersect the left [the context] and
        the right [the entity specified].  This set may be empty.
        '''
        rights = set()
        counter = 0
        for acl in entity.acls:
            if acl.action == action:
                counter = counter + 1
                if (acl.context_id in self._ctx.context_ids):
                    permissions = set(list(acl.permissions))
                    if permissions.issubset(rights):
                        '''
                        These rights have already been allowed or denied to
                        the entity, so they evaluate to a no-operation.
                        '''
                        continue
                    for right in permissions:
                        rights.add(right)
        return rights

    def flush(self):
        if self.debug:
            self.log.debug(
                'duration of implied rights was {0:.3f}'.
                format(self._implied_time))
            self.log.debug(
                'duration of asserted rights was {0:.3f}'.
                format(self._asserted_time, ))
            self.log.debug(
                'duration of revoked rights was {0:.3f}'.
                format(self._revoked_time, ))
        if self._F_perfprint:
            sys.stderr.write(
                'duration of implied rights was {0:.3f}\n'.
                format(self._implied_time, ))
            sys.stderr.write(
                'duration of asserted rights was {0:.3f}\n'.
                format(self._asserted_time, ))
            sys.stderr.write(
                'duration of revoked rights was {0:.3f}\n'.
                format(self._revoked_time, ))
        self._implied_time = 0.0
        self._asserted_time = 0.0
        self._revoked_time = 0.0

    @staticmethod
    def List(ctx, properties):
        raise NotImplementedException(
            'EntityAccessManager does not implement List')

    @staticmethod
    def ListSubquery(ctx, contexts=None, mask='r'):
        raise NotImplementedException(
            'EntityAccessManager does not implement ListSubquery')
