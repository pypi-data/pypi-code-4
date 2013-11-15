#
# Copyright (c) 2009, 2011, 2012, 2013
#  Adam Tauno Williams <awilliam@whitemice.org>
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
from bundlemanager import BundleManager


class AccessManager:
    __DebugOn__ = None
    _F_perfprint = False

    def __init__(self, ctx):
        self.log = logging.getLogger('accessmanager')
        if AccessManager.__DebugOn__ is None:
            sd = ctx.server_defaults_manager
            AccessManager.__DebugOn__ = \
                sd.bool_for_default('OGoAccessManagerDebugEnabled')
            self._F_perfprint = \
                sd.bool_for_default('CoilsCommandTimingToStdError')
        self._ctx = ctx
        self._access_managers = {}
        self._entity_rights = {}

        self._cache_checks = 0.0
        self._cache_hits = 0.0

    def flush(self):
        if self._F_perfprint and self._cache_checks:
            sys.stderr.write(
                'Cache hit rate was {0}% [{1} of {2}]\n'.
                format(self._cache_hits / self._cache_checks,
                       self._cache_hits,
                       self._cache_checks, ))
        if self._cache_checks:
            print('Cache hit rate was {0}% [{1} of {2}]\n'.
                  format(self._cache_hits / self._cache_checks,
                         self._cache_hits,
                         self._cache_checks, ))
        self._cache_checks = 0.0
        self._cache_hits = 0.0
        self._entity_rights.clear()
        for manager in self._access_managers.values():
            manager.flush()

    def entity_access_manager_for(self, kind):
        if kind not in self._access_managers:
            self._access_managers[kind] = \
                BundleManager.get_access_manager(kind, self._ctx)
        return self._access_managers[kind]

    def set_cached_access(self, entity, rights):
        self._entity_rights[entity] = rights

    def get_cached_access(self, entity):
        self._cache_checks += 1
        return self._entity_rights.get(entity, None, )

    def reduce_by_cache(self, entities):
        if not self._entity_rights:
            '''
            PERFORMANCE: Shortcircuit if the cache is empty - nothing has
            been processed yet.  This may be a common event for RPC clients
            where exactly one action occurs per transaction - an API call.
            RPC clients exhibit different performance characterstics than
            CalDAV/CardDAV or workflow clients which can perform more complex
            operations in a single transaction.
            '''
            return dict(), entities
        cached_access = {}
        uncached_entities = []
        for entity in entities:
            self._cache_checks += 1
            if entity in self._entity_rights:
                self._cache_hits += 1
                cached_access[entity] = self._entity_rights[entity]
            else:
                uncached_entities.append(entity)
        return cached_access, uncached_entities

    @property
    def debug(self):
        return AccessManager.__DebugOn__

    def filter_by_access(self, rights, entities, one_kind_hack=None, ):

        result = []

        cached_results, uncached_entities, = \
            self.reduce_by_cache(entities)

        required_rights = set(rights)

        if (not(isinstance(entities, list))):
            entities = [entities, ]

        start = time.time()

        if cached_results:
            for entity, privileges in cached_results.items():
                if required_rights.issubset(privileges):
                    result.append(entity)

        if uncached_entities:
            '''
            PERFORMANCE: The "one_kind_hack" param lets us avoid calling the
            TypeManager, which saves time [potentially a lot of time].  The
            caller can specify this when it knows for certain all the objects
            in the collection are of the specified type.  The value of the
            one_kind_hack parameter must be a valid case-sensitive entity name,
            like "Contact"
            '''

            if one_kind_hack:
                objects = {one_kind_hack: entities, }
            else:
                objects = self._ctx.type_manager.\
                    group_by_type(objects=uncached_entities, )

            for kind, entities in objects.items():
                manager = self.entity_access_manager_for(kind)
                if self.debug:
                    self.log.debug(
                        'filtering {0} using {1}'.
                        format(kind, repr(manager), ))
                x = manager.materialize_rights(objects=entities, )
                start_filter = time.time()
                '''
                BEGIN PERFORMANCE CRITICAL SECTION
                Can this be optimized?  do we need to make a list to make
                a string a set?
                '''
                for entity, privileges in x.items():
                    self.set_cached_access(entity, privileges)
                    if required_rights.issubset(privileges):
                        result.append(entity)
                    elif self.debug:
                        self.log.debug(
                            'discarding {0} due to insufficient access'.
                            format(entity, ))
                # END PERFORMANCE CRITICAL SECTION
                duration = (time.time() - start_filter)

            if self._ctx.amq_available:
                self._ctx.send(
                    None,
                    'coils.administrator/performance_log',
                    {'lname': 'access',
                     'oname': kind,
                     'runtime': duration,
                     'error': False, }, )
        if self.debug:
            self.log.debug(
                'access filter returning {0} of {1} objects'.
                format(len(result), len(entities), ))
            end = time.time()
            '''
            self.log.debug(
                '{0}: duration of filter_by_access was {1.3f}s'.
                format(repr(self), (end - start), ))
            '''
        return result

    def access_rights(self, entity, ):
        '''
        Return the current access rights for the entity.
        '''

        self._cache_checks += 1
        if entity in self._entity_rights:
            self._cache_hits += 1
            return self._entity_rights[entity]
        manager = self.entity_access_manager_for(entity.__entityName__)
        result = manager.materialize_rights(objects=[entity, ], )
        rights = result[entity]
        self.set_cached_access(entity, rights)
        return rights
