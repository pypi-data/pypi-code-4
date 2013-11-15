# Copyright (c) 2009, 2013
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
import time
import logging
from datetime import datetime
from collections import defaultdict
from exception import CoilsException
from coils.foundation import \
    ObjectInfo, Appointment, ProjectAssignment, Participant, \
    CompanyAssignment, Contact, Enterprise, Team, Project, \
    Task, Collection, CollectionAssignment, Route, \
    Document, Process, Folder, RouteGroup, ServerDefaultsManager, \
    DocumentVersion, DocumentEditing

COILS_TYPEMANAGER_CACHE = {}


class TypeManager:

    _MIME_MAP_ = None

    __slots__ = ('_log', '_orm', '_ctx', )

    def __init__(self, ctx):
        self._ctx = ctx
        self._log = logging.getLogger("typemanager")
        self._orm = self._ctx.db_session()

    def check_cache(self, object_id):
        # Expire entries
        try:
            if object_id in COILS_TYPEMANAGER_CACHE:
                return COILS_TYPEMANAGER_CACHE[object_id][0]
        except TypeError, e:
            self._log.error('objectId was {0} = {1}'.
                            format(type(object_id), object_id))
            self._log.exception(e)
        except Exception, e:
            self._log.exception(e)
        return None

    def purge_cache(self, object_id):
        if object_id in COILS_TYPEMANAGER_CACHE:
            del COILS_TYPEMANAGER_CACHE[object_id]

    def set_cache(self, object_id, kind):
        COILS_TYPEMANAGER_CACHE[object_id] = []
        COILS_TYPEMANAGER_CACHE[object_id].append(kind)
        COILS_TYPEMANAGER_CACHE[object_id].append(datetime.now())
        return kind

    @staticmethod
    def translate_kind_to_legacy(kind):
        return ObjectInfo.translate_kind_to_legacy(kind)

    @staticmethod
    def translate_kind_from_legacy(kind):
        return ObjectInfo.translate_kind_from_legacy(kind)

    def get_direntry(self, object_id):
        # TODO: Any possible way we can pre-cache the "file size"?

        class DirEntry(object):
            __slots__ = ('object_id', 'kind', 'display_name', 'file_name',
                         'size', 'owner', 'version', )

            def __init__(self, object_id, kind, display_name,
                         file_name, size, owner, version):
                self.object_id = object_id
                self.kind = kind
                self.display_name = display_name
                self.file_name = file_name
                self.size = size
                self.owner = owner
                self.version = owner

        query = self._orm.query(ObjectInfo).\
            filter(ObjectInfo.object_id == object_id)
        data = query.all()
        if data:
            data = data[0]
            dentry = DirEntry(data.object_id, data.kind, data.display_name,
                              None, 0, None, None)
        else:
            if self._ctx.amq_available:
                '''
                If the Context is on the AMQ bus ask the administrator
                service to repair/review this object-info entry.
                '''
                self._ctx.send(None,
                               'coils.administrator/repair_objinfo:{0}'.
                               format(object_id), None)
            entity = self.get_entity(object_id)
            if entity:
                version = entity.version if hasattr(entity, 'version') else 0
                display_name = entity.get_display_name() \
                    if hasattr(entity, 'get_display_name') \
                    else str(entity.object_id)
                file_name = entity.get_file_name() \
                    if hasattr(entity, 'get_file_name') \
                    else '{0}.ics'.format(object_id)
                file_size = 0
                owner_id = entity.owner_id \
                    if hasattr(entity, 'owner_id') \
                    else None
                version = entity.version if hasattr(entity, 'version') else 0
                return DirEntry(entity.object_id, entity.__entityName__,
                                display_name, file_name, file_size,
                                owner_id, version)
        return None

    def get_type(self, object_id, repair_enabled=True):
        # MEMOIZE ME!
        kind = self.check_cache(object_id)
        if (kind is None):
            query = self._orm.query(ObjectInfo).\
                filter(ObjectInfo.object_id == object_id)
            data = query.all()
            if (len(data) == 0):
                kind = self.deep_search_for_type(object_id)
                self._log.debug(
                    'Deep search for OGo#{0} discovered type {1}'.
                    format(object_id, kind))
                if ((kind != 'Unknown') and (self._ctx.amq_available)):
                    if repair_enabled:
                        self._log.debug(
                            'Requesting repair of ObjectInfo for objectId#{0}'.
                            format(object_id))
                        self._ctx.send(
                            None,
                            'coils.administrator/repair_objinfo:{0}'.
                            format(object_id), None)
                    else:
                        '''
                        If repair_enabled is False, then someone disabled
                        repair.  This is probably because we are doing a
                        looking in order to do a repair.  If repair can
                        generate repair requests then legitimately absent
                        object references will create repair-loops that
                        potentially never end.
                        '''
                        self._log.debug(
                            'Repair of ObjectInfo is disabled [OGo#{0}];'
                            ' loop prevention?'.format(object_id))
            elif (len(data) > 0):
                kind = str(data[0].kind)
        if not kind:
            return 'Unknown'
        self.set_cache(object_id, kind)
        return TypeManager.translate_kind_from_legacy(kind)

    def get_mimetype(self, entity, extension_fallback=True, ics_mode=False):
        '''
        Return a MIME type string for the entity.

        This method normalizes unknown types to "application/octet-stream".
        It will also potentially transform a recorded type of
        "binary/octet-stream" to the more common "application/octet-stream".

        :param entity: the entity to inspect.
        :param extension_fallback: Default is True. For document entities
        with an unknown type, or where the record type is octet-stream
        attempt to deduce a MIME type from the file type extension. When
        false only the explicity recorded MIME type will be considered.
        This value has no effect on any entity type other than documents.
        :param ics_mode: Default is false. If true the entity will be
        inspect to see if it supports  an iCalendar resperesentation
        such as a vCard, vEvent, etc... and if so the MIME type of that
        representation will be returned.  When false the iCalendar
        representation of the entity is ignored.
        '''

        if TypeManager._MIME_MAP_ is None:
            TypeManager._MIME_MAP_ = \
                self._ctx.server_defaults_manager.\
                default_as_dict('CoilsExtensionMIMEMap')

        if isinstance(entity, Document):
            # Check if the document has a contentType recorded via the
            # well-known contentType object property
            prop = self._ctx.pm.get_property(
                entity,
                'http://www.opengroupware.us/mswebdav',
                'contentType')
            if prop:
                mimetype = prop.get_value()
                if mimetype not in ('application/octet-stream',
                                    'binary/octet-stream',):
                    return mimetype
            if extension_fallback:
                if entity.extension:
                    return TypeManager._MIME_MAP_.\
                        get(entity.extension.lower(),
                            'application/octet-stream')

            return 'application/octet-stream'

        # Not a document

        if ics_mode and hasattr(entity, 'ics_mimetype'):
            return entity.ics_mimetype

        if hasattr(entity, 'mimetype'):
            return entity.mimetype

        return 'application/octet-stream'

    def get_entity(self, object_id, repair_enabled=True):
        kind = self.get_type(object_id, repair_enabled=repair_enabled)
        '''
        Since kind returned by get_type is a modern kind value, not a
        legecy kind value, we can use it to try to execute an implied
        Logic command
        '''
        if kind:
            if kind == 'Unknown':
                return None
            try:
                entity = self._ctx.r_c('{0}::get'.format(kind.lower()),
                                       id=object_id)
            except:
                return None
            else:
                return entity
        return None

    def get_entities(self, object_ids, limit=0, orm_hints=None):
        entities = []
        '''
        Since the kine returned as the dict key is a modern kind
        value, not a legecy kind value, we can use it to try to execute
        an implied Logic commands/
        '''
        for kind, ids in self._ctx.tm.group_ids_by_type(object_ids).items():
            try:
                result = self._ctx.r_c('{0}::get'.format(kind.lower(), ),
                                       ids=ids,
                                       orm_hints=orm_hints, )
                entities.extend(result)
            except Exception as e:
                # TODO: generate an administrative notice
                self._log.warn(
                    'attempt to use get_entities on unsupported object'
                    ' type "{0}"?'.format(kind))
                self._log.exception(e)
            else:
                if limit and len(entities) > limit:
                    break
        return entities

    def get_display_name(self, object_id):
        data = self._orm.query(ObjectInfo).\
            filter(ObjectInfo.object_id == object_id).all()
        if data:
            if data[0].display_name:
                return data[0].display_name
            entity = self.get_entity(object_id)
            if entity:
                if hasattr(entity, 'get_display_name'):
                    # Display names are limited to 127 characters
                    return entity.get_display_name()[0:127]
            return str(object_id)

    def filter_ids_by_type(self, object_ids, entity_name):
        groups = self.group_ids_by_type(object_ids)
        if (entity_name in groups):
            return groups[entity_name]
        return []

    def group_ids_by_type(self, object_ids):
        if not object_ids:
            return dict()
        result = defaultdict(list)
        query = self._ctx.db_session().\
            query(ObjectInfo).\
            filter(ObjectInfo.object_id.in_(object_ids))
        index = dict(
            (e.object_id, TypeManager.translate_kind_from_legacy(e.kind), )
            for e in query.all()
        )
        absent = set(object_ids).difference(set(index.keys()))
        for k, v in index.items():
            result[v].append(k)
        for object_id in absent:
            result[self.get_type(object_id)].append(object_id)
        return result

    def group_by_type(self, objects=None, ids=None):
        # TODO: Can the collections module do this better/faster?
        if objects:
            return self._group_objects(objects)
        elif ids:
            return self.group_ids_by_type(ids)
        else:
            raise CoilsException(
                'Neither "objects" or "ids" specified for TypeManager'
                '.group_by_type')

    def _group_objects(self, entities):
        start = time.time()
        result = defaultdict(list)
        for entity in entities:
            if entity is None:
                self._log.error(
                    'Encountered None entity while grouping objects')
            else:
                result[entity.__entityName__].append(entity)
        duration = time.time() - start
        if duration > 0.005:
            self._log.debug(
                'long duration grouping, consumed was %0.3fs'.
                format(duration))
        return result

    def deep_search_for_type(self, object_id):

        self._log.warn(
            'Performing deep search for type of OGo#{0}'.
            format(object_id))

        # Appointment
        if self._orm.query(Appointment).get(object_id):
            return 'Date'

        # Contact
        if self._orm.query(Contact).get(object_id):
            return 'Person'

        # Folder
        if self._orm.query(Folder).get(object_id):
            return 'Folder'

        # Enterprise
        if self._orm.query(Enterprise).get(object_id):
            return 'Enterprise'

        # participant
        if self._orm.query(Participant).get(object_id):
            return 'DateCompanyAssignment'

        # Project
        if self._orm.query(Project).get(object_id):
            return 'Project'

        # Team
        if self._orm.query(Team).get(object_id):
            return  'Team'

        # Task
        if self._orm.query(Task).get(object_id):
            return 'Job'

        # Document
        if self._orm.query(Document).get(object_id):
            return 'Document'

        # DocumentVersion
        if self._orm.query(DocumentVersion).get(object_id):
            return 'DocumentVersion'

        # DocumentEditing
        if self._orm.query(DocumentEditing).get(object_id):
            return 'DocumentEditing'

        # Process
        if self._orm.query(Process).get(object_id):
            return 'Process'

        # Route
        if self._orm.query(Route).get(object_id):
            return 'Route'

        # RouteGroup
        if self._orm.query(RouteGroup).get(object_id):
            return 'RouteGroup'

        if self._orm.query(Collection).get(object_id):
            return 'Collection'

        # CollectionAssignment
        if self._orm.query(CollectionAssignment).get(object_id):
            return 'collectionAssignment'

        # Hit the bottom!
        self._log.warn(
            'Deep search failed to find type for OGo#{0}', object_id)

        return None
